"""
ZKTeco ADMS (Attendance Data Management System) push endpoint.

The K40 device is configured with:
    Server Address : fagiassets.fagitone.com   (or your IP)
    Server Port    : 80

On every fingerprint punch the device makes two requests:

1. GET  /iclock/cdata?SN=<serial>&options=all&pushver=2&language=0
   -> We reply with "OK\n" to acknowledge the device is known.

2. POST /iclock/cdata?SN=<serial>&table=ATTLOG&Stamp=<last_stamp>
   Body (raw text, tab-separated rows):
       <user_id>\t<datetime>\t<verify_type>\t<status>\t0\t0\n
       ...

   status codes: 0 = Check In, 1 = Check Out, 4 = OT In, 5 = OT Out
   We map 0/4 -> punch_in  and  1/5 -> punch_out.

3. GET  /iclock/getrequest?SN=<serial>
   The device polls for commands we want to send back. We reply "OK\n"
   (no commands for now).
"""

import logging
from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from crm.models import Employee, TimeEntry, WorkSession

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ok():
    """Standard ACK reply the device expects."""
    return HttpResponse("OK\n", content_type="text/plain")


def _parse_attlog(body: str):
    """
    Parse the raw attendance log body.

    Each line: user_id\tdatetime\tverify_type\tstatus\t0\t0
    datetime format: "2026-10-05 08:30:00"
    Returns list of dicts.
    """
    records = []
    for line in body.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        try:
            user_id = parts[0].strip()
            dt_str = parts[1].strip()          # "2026-10-05 08:30:00"
            status = parts[3].strip()          # "0" check-in, "1" check-out

            # Parse naive datetime then make aware (Africa/Nairobi = UTC+3)
            naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            aware_dt = timezone.make_aware(naive_dt)

            records.append({
                "user_id": user_id,
                "timestamp": aware_dt,
                "status": status,
            })
        except (ValueError, IndexError) as exc:
            logger.warning("ZKTeco: could not parse line %r — %s", line, exc)
    return records


def _status_to_entry_type(status: str) -> str:
    """Map ZKTeco status code to our entry_type."""
    # 0 = Check In, 4 = OT In  → punch_in
    # 1 = Check Out, 5 = OT Out → punch_out
    if status in ("0", "4"):
        return "punch_in"
    return "punch_out"


def _process_record(record: dict, device_sn: str):
    """
    Find employee by zkteco_id and create TimeEntry + WorkSession.
    Skips silently if employee not found (device may have test users).
    """
    try:
        employee = Employee.objects.get(zkteco_id=record["user_id"])
    except Employee.DoesNotExist:
        logger.info(
            "ZKTeco SN=%s: no employee with zkteco_id=%r — skipping",
            device_sn, record["user_id"]
        )
        return
    except Employee.MultipleObjectsReturned:
        logger.error(
            "ZKTeco SN=%s: duplicate zkteco_id=%r — skipping",
            device_sn, record["user_id"]
        )
        return

    entry_type = _status_to_entry_type(record["status"])
    ts = record["timestamp"]
    today = ts.date()

    # Avoid duplicate entries: skip if same employee+type within 60 seconds
    duplicate = TimeEntry.objects.filter(
        employee=employee,
        entry_type=entry_type,
        timestamp__date=today,
        source="device",
        timestamp__gte=timezone.make_aware(
            datetime(today.year, today.month, today.day, ts.hour, ts.minute, 0)
        ),
    ).exists()

    if duplicate:
        logger.info(
            "ZKTeco: duplicate punch skipped for %s %s at %s",
            employee, entry_type, ts
        )
        return

    # Create the TimeEntry
    time_entry = TimeEntry.objects.create(
        employee=employee,
        entry_type=entry_type,
        timestamp=ts,
        source="device",
        notes=f"Auto from ZKTeco device {device_sn}",
    )

    # Update WorkSession
    if entry_type == "punch_in":
        work_session, created = WorkSession.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={"punch_in": ts},
        )
        if not created and not work_session.punch_in:
            work_session.punch_in = ts
            work_session.save()

    elif entry_type == "punch_out":
        try:
            work_session = WorkSession.objects.get(employee=employee, date=today)
            # Only update if this punch_out is later than the stored one
            if not work_session.punch_out or ts > work_session.punch_out:
                work_session.punch_out = ts
                work_session.calculate_hours()
        except WorkSession.DoesNotExist:
            # Device punched out without a punch-in (e.g. missed earlier push)
            WorkSession.objects.create(
                employee=employee,
                date=today,
                punch_in=ts,   # best we can do
                punch_out=ts,
            )

    logger.info(
        "ZKTeco SN=%s: recorded %s for %s at %s",
        device_sn, entry_type, employee, ts
    )


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["GET", "POST"])
def cdata(request):
    """
    /iclock/cdata

    GET  — device handshake / option request  → reply OK
    POST — device pushes attendance log        → parse & store
    """
    sn = request.GET.get("SN", "unknown")
    table = request.GET.get("table", "")

    if request.method == "GET":
        logger.info("ZKTeco handshake from SN=%s", sn)
        # Tell the device the current server time so it can self-correct
        now_str = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
        return HttpResponse(
            f"OK\nGetServerTime:{now_str}\n",
            content_type="text/plain",
        )

    # POST
    if table.upper() != "ATTLOG":
        # Other tables (OPERLOG, etc.) — acknowledge and ignore
        return _ok()

    try:
        body = request.body.decode("utf-8", errors="replace")
    except Exception as exc:
        logger.error("ZKTeco SN=%s: could not decode body — %s", sn, exc)
        return _ok()

    logger.debug("ZKTeco SN=%s ATTLOG body:\n%s", sn, body)

    records = _parse_attlog(body)
    for record in records:
        try:
            _process_record(record, sn)
        except Exception as exc:
            logger.error(
                "ZKTeco SN=%s: error processing record %r — %s",
                sn, record, exc, exc_info=True
            )

    return _ok()


@csrf_exempt
@require_http_methods(["GET"])
def getrequest(request):
    """
    /iclock/getrequest

    The device polls this URL waiting for server-side commands
    (enroll user, delete user, set time, etc.).
    We have no commands queued, so just reply OK.
    """
    sn = request.GET.get("SN", "unknown")
    logger.debug("ZKTeco getrequest from SN=%s", sn)
    return _ok()
