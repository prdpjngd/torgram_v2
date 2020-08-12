![](https://telegra.ph/file/979e1f83298c67018dd2c.png)
# #TORGRAM - Torrent Leecher
- This is Torgram Project based on the Aria2C library used for downloading/Leeching of the Torrent File with use of HerokuApp With easy Install 
- Web Client for Aria2C library
- Cloud Based Actions.
- Add magnet link and Leech torrent file
- Works like Seedr - A good alternative
- DRAWBACK : File only Stay for 30min Because after 30 min of idle state app will goes under sleep, Then Restart for next session.
- Multiple versions of torgram available Install according to your requirments.

## #Whats new in v2 of Torgram 
- Google Drive Login with Rclone Library
- "Move file to drive" Option in file manager
- New File manager
- Drive Transfers Logs Page added
- API Documentation available
- Video Player option added (Only available for .MKV & .MP4 )
- Asysncronous Loading of log data for downloading torrent links.


## #Heroku Installing Support (Easy Method)
Just Press 👉🏻 [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy) and you are done.

## #ScreenShot
![](https://telegra.ph/file/f07a260f02029c0615f10.png)

## #FAQ section ( Questions asked by users )

##### Q. Why after 30 minutes it automatically stops and files got lost ?
It is because of yout free dyno in heroku, when there is no incoming request to app. for 30 min. app go idle state automatically and then restart for new requests and all the old data got loss. 

##### Q. How large Files we can download ?
Free Dyno can have local storage of almost 350GB.

##### Q. How to setup rclone  and do I need to setup rclone on my local system before using this ?
No, you don't need to setup it locally direct login available.
##### Q. Will Torgram have v3 ?
yes, there will be

## #Torgram v3 Features ( Currently Working on It )
- "Transloadit" support (Video Converter & downloader)
- "Multiple drive" Login Option available 
- No login data lost with power of "Transfer.sh"
- get 15 Days File link with "Transfer.sh" support
- I m working on new UI for file manager.
- Unzip File Option

## #Error & Bugs ⧳
##### Do let me know if errors occur and if you can solve then fork & do contribute for this project. It will be very helpfull. 
