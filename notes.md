# Frames and video seconds
Use frames because that's what the video players we target do

# Video seconds and UTC seconds
Do not treat as the same

Robot events deltas are UTC seconds, driver timer skips are video seconds

# Information sets a match can use to fully self determine
* div type
* auton start
* auton stop
* driver start
* driver stop

OCR only
* match num
* div name
* match timer
* match mode

## Conversions
Frame time + Match Time -> Stop time
Stop time + Durations + 3 guesses -> Start time + Division Type
Stop time + Division Type + Durations -> Start time

### Unfavored conversions
driver start + frame-by-frame -> auton stop
auton stop + frame-by-frame -> driver start
