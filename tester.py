import trendy
import csv
dataset = trendy.trendyset()
dataset.nodeByDate('Date', 'allCalls.csv')
Nmax = 8
results = open('results.csv', 'wb')
DataWriter = csv.writer(results)
DataWriter.writerow(['Question Subject Monthly Breakdown'])
for node in dataset.nodes:
    groups = dataset.nodes[node].getGroupFrequency('Question Subject')
    n = 0
    for thing in sorted(groups, key=groups.get, reverse=True):
        DataWriter.writerow([str(node), thing, groups[thing]])
        n += 1
        if n == Nmax:
            break

# LinearRegression function testing:
#a, b = dataset.nodes['default'].linearRegression('temp', 'weight')
#print('%s and %s' % (a, b))
