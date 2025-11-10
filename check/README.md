# Validity Check

To ensure the validity of the website, we need to check if the website is working correctly. Script in this directory is also used to generate screenshots for the evaluation.

## Usage

Before running the script, ensure that you have set up the environment for dynamic interactive evaluation following the instructions in [envs/README.md](../envs/README.md), and run the following command to process the benchmark dataset.

```bash
cd WebDevJudge
python agent.py --do_process --base_dir /data/WebDevJudge_test
```

Then, run the following command to set up the nextjs environment.

```bash
cd WebDevJudge
bash envs/set_up_nextjs_env.sh check/workspace
```

Then, run the following command to check the validity of the website, `<display_port>` is the port of the display server, `<start_line>` and `<end_line>` are the start and end line of `webs.txt`.

```bash
cd WebDevJudge
cp webs.txt check/
cd check
nohup bash check_validality.sh 99 1 1308 > check.log 2>&1 &
```

After the script is finished, you will find the screenshots in `data/screenshots`, and the log in `check.log`, you can read the log to see if the website is working correctly.