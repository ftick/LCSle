# Worldsle
A LoL Worlds Wordle-like, found at [ftick/Worldsle](https://github.com/ftick/Worldsle)

Player data based on [Oracle's Elixir's dataset](https://oracleselixir.com/stats/players/byTournament).

Pull requests welcome!
### Running Locally
#### Requirements
* A Python 3.8+ environment

#### Running
1. Clone the repo and navigate inside the newly cloned directory.
2. Run `. venv/Scripts/activate` to activate the virtual environment
3. Navigate into the venv folder: `cd venv`
3. Rename `fake-daily.csv` to `daily.csv`: `mv fake-daily.csv daily.csv`
4. Execute `pip install -r requirements.txt` to install Python dependencies.
5. Run the application with `flask run` and enter the specified `localhost` URL.

### Deploying to Vercel
#### Requirements
* Make sure you can run the app locally first.
* A [Vercel](https://vercel.com) account.
* [Vercel CLI](https://vercel.com/cli) installed & setup.

#### Running


Execute `sls remove` to destroy the instance and all associated AWS resources.
