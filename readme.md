# Project Bedrock - Task 01

**Owner:** Paul Bassan
**Team:** Actuarial
**Type:** Documentation
**Source:** [Drive](https://drive.google.com/drive/folders/17kv08XuhP-7jW14K_n_Kgza1rGplhwC4?ogsrc=32)

## Introduction

Cytora uses machine learning to build advanced pricing models. When models behave differently to expected it is difficult to understand if this is due to the data quality or the choice of algorithms. To understand this better, a set of policies and claims have been simulated based on a universe of very simple rules. In this universe there are only 4 rating factors that affect claim frequency and severity. The volume of data is large (millions of policies, 100k’s of claims) and noise-free (noise being things like loss adjusters unfairly reducing payout sizes, lawyer fighting claims in courts and out of court settling for less than "the true" claim amount etc. etc.) which is ideal for modelling.

The objective of the exercise will be to build risk models using this data with a variety of methods. As the model of the simple universe is known, benchmarking of models built will possible - the target is well-defined and completely understood (unlike the occurrence of fires in real life).

Benefits of project - this series will form the basis of a set of data that will be useful for benchmarking model, education on how to build various models (possibly forming part of onboarding for DS).

## Data set

Contained in the data folder there are three pickle files:

- train_policies.pkl - contains a list of fire only property insurance policies
- train_claims.pkl - contains a list of fire claims with claim amounts
- test_policies.pkl - similar to (1) but a test set of policies to be used for submission

Claim frequencies - claims are modelled as Poisson

Claim amounts - log-normally distributed

## Rating factors

These are supplied along side every policy

- Trade
- Year Built
- Sprinklers
- Height of building

## Objectives

Build 3 pricing models which take as inputs: trade, year built, sprinklers, height of building and  sum insured (i.e. the policy information).

### The 3 models should be

- Simple Linear Model
- GLM
- A machine learning method

### The output of each model should be:

- Expected number of claims - E[N]
- Expected severity - E[X]

File for submission: based on the policies in test_policies.pkl, create three pickle files (1 for each model) containing a dataframe with the 3 columns below.

- The “pol_id”
- Expected frequency for each policy - labelled as “E[N]”
- Expected severity for each policy  labelled as “E[X]”

#### Example:

Naming convention for each model file:

- [YourName]-LM-01Vanilla
- [YourName]-GLM-01Vanilla
- [YourName]-ML-01Vanilla

Upload submission to: https://drive.google.com/drive/folders/1bo3DLmBTn4HjqTG6NMGkLD4L-x201y75 an example submission is in the drive, see file: “PaulBassanExample-LM-01Vanilla.pkl”

Please retain your notebooks, Seb will create a repo for these to go in.

There will be a prize for the best ML model…

Success Metrics for Project Bedrock (draft)

- Submission of all three models from every Cytorian involved in modelling work.
- Grading of risk models produced using mean squared error as the metric
- Identification of areas where training is needed (e.g. GLMs)
- Internal level of knowledge of at an individual and collective level should increase.

# Compiling answers

These steps are for the adjudication only. Access to the following folders may be restricted.

## Processing data

- Download [submissions](https://drive.google.com/drive/folders/1bo3DLmBTn4HjqTG6NMGkLD4L-x201y75?ogsrc=32) as a zip.

- Push zip file to VM

```bash
gcloud compute scp <file-name> <vm-name>:~/<final-location>
```

- [unzip](https://askubuntu.com/a/86852/753665) submissions

```bash
unzip <file-name>
```

- Download [answers](https://drive.google.com/drive/folders/1mE84l9ATZ0VYcSfzNK_dN9YqZ0jXcLha) as csv.

- Push csv to VM

```bash
gcloud compute scp <file-name> <vm-name>:~/<final-location>
```

## Evaluation

- Run script to compile results

```bash
python evaluate_submissions.py
```

- This will create a file called `SubmissionAnswers.csv`

Example:

```
model,scientist,MSE E[N],MSE E[X]
LM,PaulBassanExample,758.727,1478.6
```
