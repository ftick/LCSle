# Worldsle
A LoL Worlds Wordle-like, found at [ftick/Worldsle](https://github.com/ftick/Worldsle)

Player data based on [Oracle's Elixir's dataset](https://oracleselixir.com/stats/players/byTournament).

Pull requests welcome!

---

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

---

### Deploying to Vercel
#### Requirements
* Make sure you can run the app locally first.
* A [Vercel](https://vercel.com) account.
* [Vercel CLI](https://vercel.com/cli) installed & setup. (Make sure you're able to run `vercel help` without issue)

#### Requirements
1. Check the `requirements.txt` file for anything you might want to modify.
2. Run `vercel` to initiate a project
```
? Set up and deploy “~/path/to/repo/venv”? [Y/n] y
? Which scope do you want to deploy to? username
? Link to existing project? [y/N] n
? What’s your project’s name? venv
? In which directory is your code located? ./
> Upload [====================] 98% 0.0sNo framework detected. Default Project Settings:
- Build Command: `npm run vercel-build` or `npm run build`
- Output Directory: `public` if it exists, or `.`
- Development Command: None
? Want to override the settings? [y/N] n
```
3. To Create Production builds, run `vercel --prod`
