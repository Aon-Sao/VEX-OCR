# Event Code / Sku
* RE_STUFF

# Event Type
* VIQRC
* V5RC
* VURC

# Division Name
* Math
* Technology
* Design

# Grade / Age
* ES
* MS
* HS
* UNI

ES is IQ+  
MS is IQ+ or V5+  
HS is V5+  
UNI is VURC  
Event Code has 1 event type  
1 Event has 1 or more divisions  
Division has only 1 event type  

# Results wanted
* Start/stop frames for matches
  - Turn frame into Boxcast seconds based on boxcast fps metadata (from READB)
  - Turn frame into YouTube seconds based on ???
  - Turn frame into video seconds
* Name each match has
* Division each match belongs to
* Event Type each match belongs to
* Event SKU each match belongs to

## Stream Seconds, Frames, Video Seconds
| SS | 0 | 1  | 1.03 | 2.03 | 3.03 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| FR | 0 | 30 | 31   | 61   | 91   |
| VS | 0 | 1  | 21   | 22   | 23   |

# Existing relations
* Robot events knows Event SKU/Type pairings
* Local TM knows what division names an Event Sku has before the matches occur
  - At worlds, Local TM informs RE after unknown intervals
* Each match name is unique in the division to which it belongs
* Hand write which Boxcast stream IDs belong to which a given Division ID to READB

# Proposed flow
* RE Puller runs in background, stores on READB
  - Div name <-> Event code known at match schedule generation
* Boxcast Puller runs in background, stores on READB
  - Account, stream, channel, etc. IDs. IDs everywhere.
* Hand write to READB at event run time
* Launch OCR program
* Prefer to update READB with matches during OCR run
* Notify humans
* Publish in some manner to web
