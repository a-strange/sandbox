
# Getting the data together

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

# Evaluation

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
