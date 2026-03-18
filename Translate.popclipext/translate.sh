#!/bin/zsh

BASE_URL="${POPCLIP_OPTION_BASE_URL%/}"
API_KEY="$POPCLIP_OPTION_API_KEY"
MODEL="$POPCLIP_OPTION_MODEL"
TEXT="$POPCLIP_TEXT"

# Build JSON payload safely using python3
PAYLOAD=$(python3 -c "
import json, sys
text = sys.stdin.read()
print(json.dumps({
    'model': '$MODEL',
    'messages': [
        {
            'role': 'system',
            'content': 'You are a translator. If the input is in English, translate it to Simplified Chinese. If the input is in Chinese, translate it to English. If the input is in another language, translate it to Simplified Chinese. Only output the translation, nothing else.'
        },
        {
            'role': 'user',
            'content': text
        }
    ]
}))
" <<< "$TEXT")

# Call OpenAI-compatible API
RESPONSE=$(curl -s "${BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d "$PAYLOAD")

# Extract translation result
RESULT=$(python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data['choices'][0]['message']['content'])
except Exception as e:
    print('Error: ' + str(e))
" <<< "$RESPONSE")

# Show result in dialog (detached so PopClip doesn't wait)
osascript \
  -e 'on run argv' \
  -e '  set theText to item 1 of argv' \
  -e '  set theResult to button returned of (display dialog theText with title "Translation" buttons {"Copy", "OK"} default button "OK")' \
  -e '  if theResult is "Copy" then' \
  -e '    set the clipboard to theText' \
  -e '  end if' \
  -e 'end run' \
  -- "$RESULT" &>/dev/null &
disown
exit 0
