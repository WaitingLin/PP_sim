import csv
from tqdm import tqdm

model = "Cifar10"
mapping = "HIDR1_1"
scheduling = "Non-pipeline"

path = './statistics/'+ model + '/' + mapping + '/' + scheduling + '/64/'
new_arr = []
with open(path+'PE_utilization.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    idx = 0
    scale = 5
    for row in tqdm(csv_reader):
        if idx <= 20000:
            if idx % scale == 0:
                new_arr.append(row)
        else:
            new_arr.append(row)
        idx += 1

with open(path+'Scale_PE_utilization.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in tqdm(new_arr):
        writer.writerow(row)
