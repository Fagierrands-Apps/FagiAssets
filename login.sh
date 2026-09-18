#!/bin/bash
USERNAME=$1
PASSWORD=$2

rm -f /tmp/c.txt
curl -s -c /tmp/c.txt https://fagiassets.fagitone.com/login/ > /dev/null
TOKEN=$(grep csrftoken /tmp/c.txt | awk '{print $7}')

RESULT=$(curl -s -b /tmp/c.txt -c /tmp/c.txt \
  -X POST https://fagiassets.fagitone.com/login/ \
  -H "Referer: https://fagiassets.fagitone.com/login/" \
  -d "username=$USERNAME&password=$PASSWORD&csrfmiddlewaretoken=$TOKEN" \
  -w "%{http_code}" -o /dev/null)

if [ "$RESULT" = "302" ]; then
  echo "✅ $USERNAME - LOGIN SUCCESS"
else
  echo "❌ $USERNAME - LOGIN FAILED (status: $RESULT)"
fi
