# Installation
1. Clone the repo
```
git clone git@github.com:notrandomath/job-fetcher.git
cd job-fetcher
```
2. Create new conda environment
```
conda create -n job_fetcher python=3.10.9 -y
conda activate job_fetcher
```
3. Install Dependencies
```
pip install -r requirements.txt
```
4. Create API Key
Go to [Google AI Studio](https://aistudio.google.com/api-keys) and create an API key then
run the following
```
echo "GEMINI_API_KEY=<YOUR API KEY>" > .env
```
5. Put the `All_Projects_Master_Resume.pdf` file in the repo folder (case sensitive)
# Run
To run, do the following:
```
conda activate job_fetcher
python fetch_jobs.py
```
After running, the results will automatically open in your web browser. You will be limited to 5 or so calls per day with the free plan. You may have to call it multiple times as Gemini sometimes doesn't return anything. 