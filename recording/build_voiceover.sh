#!/usr/bin/env bash
# Build the Subscription Ghost voiceover with Amazon Polly neural.
# Synths each segment as SSML, measures it, places it at its start time, mixes a quiet
# ambient bed under it, and writes voiceover.wav + soundtrack.wav.
# Usage: bash recording/build_voiceover.sh
set -euo pipefail
cd "$(dirname "$0")"
VOICE="${POLLY_VOICE:-Matthew}"
REGION="us-east-1"
OUT=voiceover
mkdir -p "$OUT"

say () {  # $1 = id, $2 = ssml text
  aws polly synthesize-speech --region "$REGION" --engine neural --voice-id "$VOICE" \
    --output-format mp3 --text-type ssml --text "$2" "$OUT/$1.mp3" >/dev/null
  ffmpeg -y -i "$OUT/$1.mp3" -ar 44100 -ac 2 "$OUT/$1.wav" >/dev/null 2>&1
  local d; d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUT/$1.wav")
  echo "  $1: ${d}s"
}

echo "Synthesizing segments with Polly ($VOICE)..."
say seg1 '<speak>There is money leaving your account every month, <break time="200ms"/> and you probably have not noticed.</speak>'
say seg2 '<speak>I upgraded to Airtel Black, got Amazon Prime free for a year, <break time="150ms"/> then got billed fifteen hundred rupees for video I have never watched. I only use it for shipping.</speak>'
say seg3 '<speak>Subscription Ghost caught it. <break time="150ms"/> The four hundred rupee shopping plan covers what I actually use. That is eleven hundred rupees a year, back in my pocket.</speak>'
say seg4 '<speak>It is an open model that reads your subscriptions and predicts which ones are ghosts: <break time="150ms"/> the plan too big for you, the price that crept up, the gym you quit in February.</speak>'
say seg5 '<speak>The whole thing is open source. <break time="150ms"/> TabPFN does the prediction, Gemma writes the verdict, and every rupee is computed from a real price list, never invented.</speak>'
say seg6 '<speak>Add your own in two taps. Pick a service, say how often you really use it, and it ranks it instantly. <break time="150ms"/> No bank login. Nothing is uploaded. It runs on your laptop for free.</speak>'
say seg7 '<speak>Hit stop the leak, <break time="150ms"/> and watch the money come back. On this sample, twenty nine thousand rupees a year was quietly bleeding out.</speak>'
say seg8 '<speak>And it is honest about being wrong. It tells you the three real ghosts it still missed, <break time="150ms"/> because a money tool that hides its mistakes is not worth trusting.</speak>'
say seg9 '<speak>Try it, the link is in the description. If this found a ghost in your subscriptions, <break time="150ms"/> like, comment, and share, and follow for more open source AI builds.</speak>'

# start times (seconds) matching SCRIPT.md, spaced so no line overruns the next
declare -A START=( [seg1]=0.0 [seg2]=6.0 [seg3]=16.0 [seg4]=25.5 [seg5]=35.0 [seg6]=45.0 [seg7]=57.0 [seg8]=66.0 [seg9]=75.5 )
TOTAL=88

echo "Placing segments on one timeline..."
IN=(); FILTERS=(); MIX=""; i=0
for s in seg1 seg2 seg3 seg4 seg5 seg6 seg7 seg8 seg9; do
  IN+=( -i "$OUT/$s.wav" )
  ms=$(python3 -c "print(int(${START[$s]}*1000))")
  FILTERS+=( "[$i:a]adelay=${ms}|${ms}[a$i];" )
  MIX+="[a$i]"
  i=$((i+1))
done
ffmpeg -y "${IN[@]}" -filter_complex "${FILTERS[*]}${MIX}amix=inputs=$i:normalize=0,apad[vo]" \
  -map "[vo]" -t "$TOTAL" "$OUT/voiceover.wav" >/dev/null 2>&1
echo "  wrote $OUT/voiceover.wav (${TOTAL}s)"

echo "Building a quiet original ambient bed (A2 + E3 drone, faded)..."
ffmpeg -y -f lavfi -i "sine=frequency=110:duration=$TOTAL" -f lavfi -i "sine=frequency=164.81:duration=$TOTAL" \
  -filter_complex "[0:a]volume=0.5[a];[1:a]volume=0.32[b];[a][b]amix=inputs=2:normalize=0,tremolo=f=0.12:d=0.5,lowpass=f=600,volume=0.09,afade=t=in:st=0:d=2.5,afade=t=out:st=$(python3 -c "print($TOTAL-4.5)"):d=4.3[bed]" \
  -map "[bed]" -ac 2 "$OUT/bed.wav" >/dev/null 2>&1

echo "Mixing voice + bed -> soundtrack.wav..."
ffmpeg -y -i "$OUT/voiceover.wav" -i "$OUT/bed.wav" \
  -filter_complex "amix=inputs=2:normalize=0,afade=t=out:st=$(python3 -c "print($TOTAL-3.6)"):d=3.6" \
  -t "$TOTAL" "$OUT/soundtrack.wav" >/dev/null 2>&1

echo "Done. soundtrack.wav is ready to mux onto the silent screen capture."
echo "Next: record silent video per SCRIPT.md, then:"
echo "  ffmpeg -y -i silent.mp4 -i $OUT/soundtrack.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest tmp.mp4"
echo "  ffmpeg -y -i tmp.mp4 -c:v copy -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a aac -b:a 192k -movflags +faststart final.mp4"
