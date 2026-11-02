# Cyber Threat Mapper

Maps text from cyber threat intelligence reports to [MITRE ATT&CK](https://attack.mitre.org/) techniques using embedding-based semantic search.

> **Status:** In progress. Retrieval works end to end. Accuracy measurement and an LLM re-ranking step are next.

## The problem

Security teams tag threat reports with ATT&CK techniques so they can track attacker behavior and plan detections. Doing this by hand is slow, and keyword search misses matches when a report's wording differs from ATT&CK's. A report might say "the backdoor restarted every time the machine booted" while the technique is named "Boot or Logon Autostart Execution."

Asking an LLM directly doesn't solve it either. In testing, a small local model (`gemma3:1b`) was asked which technique matches "an attacker created a scheduled task so their malware runs again after restart." It answered **T1003** every time, which is actually OS Credential Dumping, under made-up names. The correct answer is **T1053.005, Scheduled Task**.

## How it works

1. **Load:** Reads MITRE's Enterprise ATT&CK data (STIX format) and keeps the 706 current techniques and sub-techniques, filtering out revoked and deprecated ones.
2. **Embed:** Converts each technique's name and description into a 768-number embedding with `nomic-embed-text`, run locally through [Ollama](https://ollama.com). This runs once, and the results are saved.
3. **Search:** Embeds the input text the same way, scores it against every technique with cosine similarity, and returns the top 5.

Everything runs locally. No API keys, no model training.

## Example results

```
$ python src/step03_search.py "the attacker encrypted all the files"
  1. T1486      Data Encrypted for Impact          score 0.755
  2. T1027.013  Encrypted/Encoded File             score 0.744
  3. T1027      Obfuscated Files or Information    score 0.739
```
T1486 is the ATT&CK technique for ransomware.

```
$ python src/step03_search.py "the attacker dumped password hashes from memory"
  1. T1110.002  Password Cracking                  score 0.751
  2. T1003      OS Credential Dumping              score 0.726
  3. T1550.002  Pass the Hash                      score 0.725
```
The correct technique appears at #2, and every result is credential-related.

**Known weakness:** for "the backdoor would start again automatically every time the computer was restarted," 4 of the top 5 results are Persistence techniques, but the best match (T1547, Boot or Logon Autostart Execution) is missing. One likely cause is citation tags and links in MITRE's descriptions adding noise to the embeddings.

## Setup (macOS)

Requires Python 3.10+ and [Ollama](https://ollama.com/download).

```bash
# Models
ollama pull nomic-embed-text
ollama pull gemma3:1b        # only needed for step01

# Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# ATT&CK data (about 53 MB, not stored in this repo)
mkdir -p data/raw
curl -L -o data/raw/enterprise-attack.json https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json
```

## Usage

```bash
python src/step02_load_attack.py         # extract and filter techniques
python src/step03_embed_techniques.py    # embed all techniques (one time)
python src/step03_search.py "text from a threat report"
```

## Tests

```bash
python -m pytest
```
14 unit tests cover the data loader, cosine similarity, and ranking. They use small fake data, so Ollama doesn't need to be running.



## Data source

Uses [MITRE ATT&CK](https://attack.mitre.org/) Enterprise data from [mitre-attack/attack-stix-data](https://github.com/mitre-attack/attack-stix-data). ATT&CK® is a registered trademark of The MITRE Corporation.