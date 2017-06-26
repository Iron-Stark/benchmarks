'''
  @file random_forest.py

  Classifier implementing the Random Forest classifier with shogun.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

#Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
  sys.path.insert(0, metrics_folder)

from log import *
from timer import *
from definitions import *
from misc import *

import numpy as np
from modshogun import RealFeatures, MulticlassLabels, RandomForest, EuclideanDistance, MajorityVote

'''
This class implements the decision trees benchmark.
'''
class RANDOMFOREST(object):

  '''
  Create the Random Forest Classifier benchmark instance.
  @param dataset - Input dataset.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.form = 1
    self.numTrees = 10

  '''
  Build the model for the Random Forest Classifier.
  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels, options):
    mVote = MajorityVote()
    randomForest = RandomForest(data, labels, self.numTrees)
    randomForest.set_combination_rule(mVote)
    randomForest.train()

    return randomForest

  '''
  Use the shogun libary to implement the Random Forest Classifier.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RandomForestShogun(self, options):
    def RunRandomForestShogun(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      trainData = RealFeatures(trainData.T)
      labels = MulticlassLabels(labels)
      testData = RealFeatures(LoadDataset(self.dataset[1]).T)

      # Number of Trees.
      n = re.search("-n (\d+)", options)
      # Number of attributes to be chosen randomly to select from.
      f = re.search("-f (\d+)", options)

      self.form = 1 if not f else int(f.group(1))
      self.numTrees = 10 if not n else int(n.group(1))

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels, options)
          # Run the Random Forest Classifier on the test dataset.
          self.predictions = self.model.apply_multiclass(testData)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunRandomForestShogun, self.timeout)

  '''
  Perform the classification using Random Forest. If the method has been
  successfully completed return the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
      Log.Info("Perform Random Forest.", self.verbose)

      if len(self.dataset) >= 2:
        results = self.RandomForestShogun(options)
      else:
        Log.Fatal("This method requires at least two datasets.")

      metrics = {'Runtime' : results}
      if len(self.dataset) >= 3:
       # Check if we need to create a model.
       if not self.model:
         trainData, responses = SplitTrainData(self.dataset)
         self.model = self.BuildModel(RealFeatures(trainData.T), MulticlassLabels(labels), options)
         self.predictions = self.model.apply_multiclass(RealFeatures(LoadDataset(self.dataset[1]).T))
        
       if self.predictions:
        testData = LoadDataset(self.dataset[1])
        truelabels = LoadDataset(self.dataset[2])

        confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)

        metrics['Avg Accuracy'] = Metrics.AverageAccuracy(confusionMatrix)
        metrics['MultiClass Precision'] = Metrics.AvgPrecision(confusionMatrix)
        metrics['MultiClass Recall'] = Metrics.AvgRecall(confusionMatrix)
        metrics['MultiClass FMeasure'] = Metrics.AvgFMeasure(confusionMatrix)
        metrics['MultiClass Lift'] = Metrics.LiftMultiClass(confusionMatrix)
        metrics['MultiClass MCC'] = Metrics.MCCMultiClass(confusionMatrix)
        metrics['MultiClass Information'] = Metrics.AvgMPIArray(confusionMatrix, truelabels, self.predictions)
        metrics['Simple MSE'] = Metrics.SimpleMeanSquaredError(truelabels, self.predictions)

      return metrics
