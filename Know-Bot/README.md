# Know-Bot
## Shalin Mehta (sjm382) | Eric Sun (ejs336) | Junghwan (Peter) Oh (jo299)

## AI Prac Fall 2019 Project

## How to run

Open the folder in command line and type `python knowbot.py`

Running the python file can take a while to initalize, since it's loading all
the sentence embeddings. On the first run it should take about 5 minutes.
Afterwards, it should take about 2 minutes.

Please ensure that nltk, spacy, sklearn, numpy, sister are installed

## Datasets

onlyTopicsData goes to each Wikipedia article for each topic (mathematics,
science, music, politics, history, CS) then scrapes each link

Format:
+ Dictionary of dictionary
+ first key is overarching topic: mathematics, science, music
  + value is dictionary
+ second dictionary: key is inside topic: ex. george washington
  + value is text

Example:
{ "mathematics" : { "euler" : "Euler is a pretty cool dude"},
  "history" : { "george washington" : "george washington was a president"}
}