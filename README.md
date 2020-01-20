# telegram-bot

This bot helps Telegram users find ATMs which are near the user's location.  
Applies to ATMs in Buenos Aires, Argentina.

## Usage
- `/link`: asks for LINK ATMs near user location
- `/banelco`: asks for BANELCO ATMs near user location

After the user sends a command, the bot will ask the user for a GPS location. The result is an image of a map, with the user 
location sent, and the ATMs locations. The addresses are also sent as text. The commands are case insensitive.

## Running the bot
- The app is containerized. Related commands located in `run-outside.sh` and `run-inside.sh`
- Before launching the bot, generate a token with the BotFather, and include it as an environment variable in the Dockerfile. The
existing one is revoked

## Additional Features
The bot also performs an estimation of remaining cash availability, given the asumption that users mostly visit ATMs according
to the following probability:
 - 1st nearest ATM: 70%
 - 2nd nearest ATM: 20%
 - 3rd nearest ATM: 10%

There is also a cron job which represents ATM refill. This event is performed every day at 8 AM, during Monday to Friday.
