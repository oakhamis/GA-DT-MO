"""
Bank Feature Selection
"""

import pandas as pd 
import numpy as np 
import sklearn

from lightgbm import *
from sklearn.model_selection import *
from sklearn.naive_bayes import *
from genetic_selection import GeneticSelectionCV
from sklearn.metrics import *
from sklearn.model_selection import *

from sklearn.tree import *
import warnings
from sklearn.utils import *
import matplotlib.pyplot as plt
import itertools
import DataTable
from statistics import mean

warnings.filterwarnings("ignore")

mcc = make_scorer(matthews_corrcoef)

"""# Data Preprocessing"""

import os

os. getcwd()

os.chdir('C:/Users\Omar\Desktop\Spring 2020\Modern Optimization\Assessment\ML_GA\GA_python')

data = pd.read_csv('bank-full.csv')

data_col = data.dtypes.pipe(lambda x: x[x == 'object']).index
label_mapping = {}

for c in data_col:
    data[c], label_mapping[c] = pd.factorize(data[c])

print(label_mapping)
x = data.drop('y', axis=1)
y = data['y']

allfeats = x.columns
allfeats = list(allfeats)
print(allfeats)
numcols = set(allfeats)
numcols = list(numcols)

from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3, random_state=101)
x_train.shape, x_test.shape, y_train.shape, y_test.shape

from sklearn import tree
clf = tree.DecisionTreeClassifier()
clf = clf.fit(x_train, y_train)

tree.plot_tree(clf,max_depth=1)

y_pred = clf.predict(x_test)
accuracy_score(y_test, y_pred, normalize=False)/x_test.shape[0]

estimator = tree.DecisionTreeClassifier()


report = pd.DataFrame()
nofeats = [] 
chosen_feats = [] 
cvscore = [] 

rkf = RepeatedStratifiedKFold(n_repeats = 30, n_splits = 3)
# pop_size =[50,100,150]
pop_size =[50]
cross_over=[0.2,0.5,0.8]
mutation = [0.01,0.05,0.1]
variations = [i for  i in itertools.product(pop_size,cross_over,mutation)]
run = 0 
best_fitness_values = [0]*len(variations)
for var_index ,var in enumerate(variations):
  bsf_score_run = 0
  selector = GeneticSelectionCV(estimator,
                                  cv = rkf,
                                  verbose = 0,
                                  scoring = "accuracy",
                                  max_features = len(allfeats),
                                  n_population = var[0],
                                  crossover_proba = var[1],
                                  mutation_proba = var[2],
                                  n_generations = 30,
                                  crossover_independent_proba=0.5,
                                  mutation_independent_proba=0.1,
                                  #tournament_size = 3,
                                  n_gen_no_change=10,
                                  caching=True,
                                  n_jobs=-1)
  for i in range(30):
    print("-------------------------run {} ----------------------".format(i))
    
    selector  = selector.fit(x_train, y_train)
    run+=1
    genfeats = data[allfeats].columns[selector.support_]
    genfeats = list(genfeats)
    print("Chosen Feats:  ", genfeats)

    cv_score = selector.generation_scores_[-1]
    if cv_score > bsf_score_run:
      bsf_score_run = cv_score
      bsf_score_index = run
      best_fitness_values[var_index] = selector.generation_scores_
      
    nofeats.append(len(genfeats)) 
    chosen_feats.append(genfeats) 
    cvscore.append(cv_score)
    
report["No of Feats"] = nofeats
report["Chosen Feats"] = chosen_feats
report["Scores"] = cvscore

# for i,fitness_values in  enumerate(best_fitness_values):
#     plt.plot(fitness_values, label='GA variation'+ str(i))
# plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
# plt.ylim((0.8825,0.895))

max_fitness_value = [max(i) for i in best_fitness_values[0:9]]

avg_fitness_value = [mean(i) for i in best_fitness_values[0:9]]


index = np.argsort(max_fitness_value) 

index = index[::-1]

avg_index = index = np.argsort(avg_fitness_value)

avg_index = avg_index[::-1]



vars_ = ['Pop. Size '+ str(vara[0]) + ' / Crossover rate '+ str(vara[1]) + ' / Mutation rate ' + str(vara[2]) for vara in variations]
for i in  index:
    plt.plot(best_fitness_values[i], label=vars_[i])
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1))
plt.ylim((0.883,0.8936))
plt.rcParams["figure.figsize"] = (7,7)
fig.subplots_adjust(bottom=0.25)



report_final = report.iloc[0:270].copy()

report_final["Scores"] = np.round(report_final["Scores"], 6)
report_final.sort_values(by = "Scores", ascending = False, inplace = True)
#report.index
ga_feats = report_final.iloc[0]["Chosen Feats"]
print(ga_feats)

report_final.to_csv("GA_report.csv",index=False)

# Standerd error calculation for each variation:
       
First_std_err = np.std(report.iloc[30:60]['Scores']) / np.sqrt(len(report.iloc[30:60]))
Second_std_err = np.std(report.iloc[150:180]['Scores']) / np.sqrt(len(report.iloc[150:180]))   
Third_std_err = np.std(report.iloc[240:270]['Scores']) / np.sqrt(len(report.iloc[240:270]))  
   
   
# Error Plot / Figure 3 in the report.
plt.figure(figsize=(20,20))
generation = [x for x in range(len(report.iloc[240:270]))]
fig, ax = plt.subplots()
ax.errorbar(generation, report.iloc[30:60]['Scores'],yerr = First_std_err, solid_capstyle='projecting', capsize=2,label='Population size:50, Crossover Rate: 0.8, Mutation Rate:0.1')
ax.errorbar(generation, report.iloc[150:180]['Scores'],yerr = Second_std_err, solid_capstyle='projecting', capsize=2,label='Population size:50, Crossover Rate: 0.5, Mutation Rate:0.1')
ax.errorbar(generation, report.iloc[240:270]['Scores'],yerr = Third_std_err, solid_capstyle='projecting', capsize=2,label='Population size:50, Crossover Rate: 0.2, Mutation Rate:0.05')
plt.xlabel('Generation')
plt.ylabel('Fitness Value')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1))
ax.grid(alpha=0.5, linestyle=':')
plt.show()



# from evolutionary_search import EvolutionaryAlgorithmSearchCV
# # Define the hyperparameter configuration space
# '''
# rf_params = {
#     'n_estimators': np.logspace(1,1.8,num = 10 ,base=20,dtype='int'),
#     'max_depth': np.logspace(1,2,num = 10 ,base=10,dtype='int'),
#     "max_features":np.logspace(0.2,1,num = 5 ,base=8,dtype='int'),
#     "min_samples_split":np.logspace(0.4, 1, num=5, base=10, dtype='int'), #[2, 3, 5, 7, 10],
#     "min_samples_leaf":np.logspace(0.1,1,num = 5 ,base=11,dtype='int'),
#     "criterion":['gini','entropy']
# }
# '''
# rf_params = {
#     #"max_features":range(0,13),
#     'max_depth': range(5,50),
#     "min_samples_split":range(2,11),
#     "min_samples_leaf":range(1,11),
#     #Categorical(name='criterion', categories=['gini','entropy'])#
#     "criterion":['gini','entropy']
# }
# estimator = tree.DecisionTreeClassifier()
# print(estimator.get_params().keys())
# # Set the hyperparameters of GA 
# ga1 = EvolutionaryAlgorithmSearchCV(estimator=clf,
#                                    params=rf_params,
#                                    scoring="accuracy",
#                                    cv=3,
#                                    verbose=1,
#                                    population_size=10,
#                                    gene_mutation_prob=0.10,
#                                    gene_crossover_prob=0.5,
#                                    tournament_size=3,
#                                    generations_number=5,
#                                    n_jobs=1)
# ga1.fit(x_train, y_train)
# print(ga1.best_params_)
# print("Accuracy:"+ str(ga1.best_score_))

# print(ga1.all_history_[0])
# #plt.plot(selector.generation_scores_)