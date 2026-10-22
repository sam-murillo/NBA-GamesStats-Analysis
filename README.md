# NBA-GamesStats-Analysis
Project Purpose: The purpose of this project is addressing curiosity about what stats matter in an NBA game and lead to the team winning or losing. My intended audience is NBA and sports fans. The data I am using is a dataset from Kaggle that was scraped from the NBA's website of their official data. The main analytical goal of the project is to show what aspects of the game have a statistical impact on the outcome of the game to show how different actions affect success. In my app, a user should explore and compare how different actions and stats affect the outcomes of games and the success of the team. One important limit of boundary of the project is that the play style of the game of basketball changes over time so there may not be universal strengths but better strategies in the different time periods.

Data access: My data was sourced from Kaggle. Within the Kaggle, I am specifically using the "TeamStatisticsExtended.csv" the link to the Kaggle is: https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores/data 

Streamlit is at this link: https://nba-gamesstats-analysis.streamlit.app/

Setup Instructions: Download the analysis notebook and the dataset to your computer and run it in Jupyter lab. To see the streamlit, visit the link above.

Key Limitations: The conclusions I reached are more of a “what” and less of a “why”. I have shown there is a positive correlation between rebound percentage and turnovers, and I have ideas about why that is, but my data and analysis have not proved that. This makes the major limitation of my project the fact that it reveals very interesting relationships, but not why they exist or what to do with the information.

AI-Use Disclosure: I used AI to debug Python code, research some Python code, and to write the code of the Streamlit application. A representative prompt for debugging is "what does this error message mean, here is the code I tried to run". A representative prompt for researching code is "what parameters does the seaborn KDE plot take". A representative prompt for writing the Streamlit application is "Make a heatmap comparing the Pearson correlation of the features in this data frame, and add it as a tab in the Streamlit application" The model I used was Claude Opus 5.5. The model I used was Claude Opus 5.5

Streamlit prompt rough guideline:
"Hello, I would like help building a streamlit application for a school project. I am not familiar with streamlit so I will need a lot of help with coding, but I want the ideas to be my own and for you to help me to write and understand the code. My project is exploring NBA game by game data to see what influences winning and how different statistics are correlated. I have the data set, sourced from Kaggle, in ____ file with ____ as my parameters of interest. It is currently running locally on Jupyter lab, but eventually it will need to be deployed."

I also provided it with relevant code from my analysis, for example: " this is how i got the years out of the date time, which we will need for our app 
#converting date time to year for later analysis 
df2["year"] = df2["gameDateTimeEst"].astype(str).str[:4].astype(int)
df2.drop(columns=["gameDateTimeEst"], inplace=True) "

These two types of prompts and the prompt above can be used to have AI assist you in making your own streamlit application for your own projects :)
