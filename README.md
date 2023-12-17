# dbot

Discord bot with a variety of capabilities.

| Command       | Description                                             |
| ------------- | ------------------------------------------------------- |
| 8ball         | Fortunes from beyond.                                   |
| chat          | Interacts with an AI chat assistant.                    |
| choose        | Chooses between multiple choices.                       |
| define        | Define a term.                                          |
| inspire       | For when you need a pick-me-up.                         |
| joined        | Says when a member joined.                              |
| ping          | Pokes dbot to see if she's awake.                       |
| roll          | Rolls a dice in NdN format.                             |
| balance       | Display an account balance                              |
| tip           | Tip another account                                     |
| bank          | Interact with the bank                                  |
| + accounts    | List bank accounts and their balances                   |
| + openaccount | Create an account                                       |
| + help        | HELP for the bank commands                              |
| stock         | Interact with the stock market                          |
| + buy         | Buy stock                                               |
| + create      | Create and add a new stock to the market                |
| + holdings    | List stock holdings                                     |
| + list        | List the stocks on the market                           |
| + sell        | Sell stock                                              |
| + help        | HELP for the stock commands                             |
| help          | Shows the main help menu                                |
| yell          | Not a command, but if you 'YELL' dbot will 'YELL' back. |

## Setup

### Install required dependencies

To bootstrap your environment run `setup.sh` to install python3, pip3, and the packages required to run dbot.

### Configure dbot

In `config/.env` you can customize dbot:

- `DISCORD_TOKEN`: Your bot's authN token
- `COMMAND_PREFIX`: Command(s) that will trigger the bot.
- `COMMAND_WITH_SPACE`: Whether or not to require a space ofter the trigger command. `True` or `False`. e.g. `!ping` vs `! ping`.
- `BRAIN_PATH`: Path to the data files that will be used as dbot's brain. This can be the path to the `data` directory.

#### Customize data files (optional)

You can customize the data in the `data` directory to your liking. There is sample data pre-populated that you can run with as well:

- `data/fortunes.json` - List of 8-ball style fortunes
- `data/statuses.json` - Discord statuses the bot will rotate through
- `data/stocks.json` - List of stocks on the market
- `data/yell.json` - List of responses dbot can use when a member types a message in 'ALL CAPS'. Dbot will save all 'YELLED' messages from channel members and save them in this list.
- `data/yell_blacklist.json` - List phrases that will not be saved by dbot. You can put a list of profane or offensive words here.

You can also save the data dbot uses to a custom directory to avoid conflicting with the `data` directory that is checked into git.

e.g. Make a new `brain` directory, copy the contents of `data` to `brain` to avoid dbot from overwriting the default data and update `BRAIN_PATH` in `config/.env` to the new directory.

## Running

To run dbot simply run `start_bot.sh` after she is configured.

Discord logs can be found in `logs/discord.log`. Any other output (stdout/stderr) will be in `logs/app.log`.

Run `pkill -f dbot.py` to stop dbot (the bots must be stopped).
