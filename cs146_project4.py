# -*- coding: utf-8 -*-
"""Qianchi Huang CS146-PROJECT4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NPP9-bkVoL191e3s5fY1PK3iYXEgdcOx

# PCA and k-means

## Setting up
"""

"""
Author      : Yi-Chieh Wu, Sriram Sankararaman, Qianchi Huang
"""

# numpy and scipy libraries
import numpy as np
from scipy import stats
import collections

# matplotlib libraries
import matplotlib.pyplot as plt

# To add your own Drive Run this cell.
from google.colab import drive
drive.mount('/content/gdrive')

import sys
# Change the path below to the path where your folder locates
# where you have util.py
### ========== TODO : START ========== ###
sys.path.append('/content/gdrive/My Drive/')
### ========== TODO : START ========== ###

import util
from util import *

"""## Point, Cluster and Set of Clusters classes"""

######################################################################
# classes
######################################################################

class Point(object) :
    
    def __init__(self, name, label, attrs) :
        """
        A data point.
        
        Attributes
        --------------------
            name  -- string, name
            label -- string, label
            attrs -- string, features
        """
        
        self.name = name
        self.label = label
        self.attrs = attrs
    
    
    #============================================================
    # utilities
    #============================================================
    
    def distance(self, other) :
        """
        Return Euclidean distance of this point with other point.
        
        Parameters
        --------------------
            other -- Point, point to which we are measuring distance
        
        Returns
        --------------------
            dist  -- float, Euclidean distance
        """
        # Euclidean distance metric
        return np.linalg.norm(self.attrs-other.attrs)
    
    
    def __str__(self) :
        """
        Return string representation.
        """
        return "%s : (%s, %s)" % (self.name, str(self.attrs), self.label)

class Cluster(object) :
    
    def __init__(self, points) :
        """
        A cluster (set of points).
        
        Attributes
        --------------------
            points -- list of Points, cluster elements
        """        
        self.points = points
    
    
    def __str__(self) :
        """
        Return string representation.
        """
        s = ""
        for point in self.points :
            s += str(point)
        return s
        
    #============================================================
    # utilities
    #============================================================
    
    def purity(self) :
        """
        Compute cluster purity.
        
        Returns
        --------------------
            n           -- int, number of points in this cluster
            num_correct -- int, number of points in this cluster
                                with label equal to most common label in cluster
        """        
        labels = []
        for p in self.points :
            labels.append(p.label)
        
        cluster_label, count = stats.mode(labels)
        return len(labels), np.float64(count)
    
    
    def centroid(self) :
        """
        Compute centroid of this cluster.
        
        Returns
        --------------------
            centroid -- Point, centroid of cluster
        """

        # set the centroid label to any value (e.g. the most common label in this cluster)
        
        labels = []
        for p in self.points :
            labels.append(p.label)
        cluster_label, count = stats.mode(labels)

        c_attrs = np.array([point.attrs for point in self.points])
        index = np.sum(c_attrs, axis=0)/len(self.points)

        centroid = Point('C', cluster_label[0], index)
        return centroid

    
    
    def medoid(self) :
        """
        Compute medoid of this cluster, that is, the point in this cluster
        that is closest to all other points in this cluster.
        
        Returns
        --------------------
            medoid -- Point, medoid of this cluster
        """
        

        distances = {}

        # find distance of each point to all other points except itself
        for p in self.points:
            distances[p] = []
            for other in self.points:
                if other != p: 
                    distances[p].append(p.distance(other))

        # find the avg distance of each point to other points
        for key, value in distances.items():
            mean = np.mean(value)
            distances[key] = mean

        # get point with minimum avg distance
        medoid = min(distances, key=distances.get)
        return medoid

    
    
    def equivalent(self, other) :
        """
        Determine whether this cluster is equivalent to other cluster.
        Two clusters are equivalent if they contain the same set of points
        (not the same actual Point objects but the same geometric locations).
        
        Parameters
        --------------------
            other -- Cluster, cluster to which we are comparing this cluster
        
        Returns
        --------------------
            flag  -- bool, True if both clusters are equivalent or False otherwise
        """
        
        if len(self.points) != len(other.points) :
            return False
        
        matched = []
        for point1 in self.points :
            for point2 in other.points :
                if point1.distance(point2) == 0 and point2 not in matched :
                    matched.append(point2)
        return len(matched) == len(self.points)

class ClusterSet(object):

    def __init__(self) :
        """
        A cluster set (set of clusters).
        
        Parameters
        --------------------
            members -- list of Clusters, clusters that make up this set
        """
        self.members = []
    
    
    #============================================================
    # utilities
    #============================================================    
    
    def centroids(self) :
        """
        Return centroids of each cluster in this cluster set.
        
        Returns
        --------------------
            centroids -- list of Points, centroids of each cluster in this cluster set
        """
        
        centroids = []
        for cluster in self.members:
          centroids.append(cluster.centroid())
        return centroids

    
    
    def medoids(self) :
        """
        Return medoids of each cluster in this cluster set.
        
        Returns
        --------------------
            medoids -- list of Points, medoids of each cluster in this cluster set
        """

        medoids = []
        for cluster in self.members:
          medoids.append(cluster.medoid())
        return medoids

    
    
    def score(self) :
        """
        Compute average purity across clusters in this cluster set.
        
        Returns
        --------------------
            score -- float, average purity
        """
        
        total_correct = 0
        total = 0
        for c in self.members :
            n, n_correct = c.purity()
            total += n
            total_correct += n_correct
        return total_correct / float(total)
    
    
    def equivalent(self, other) :
        """ 
        Determine whether this cluster set is equivalent to other cluster set.
        Two cluster sets are equivalent if they contain the same set of clusters
        (as computed by Cluster.equivalent(...)).
        
        Parameters
        --------------------
            other -- ClusterSet, cluster set to which we are comparing this cluster set
        
        Returns
        --------------------
            flag  -- bool, True if both cluster sets are equivalent or False otherwise
        """
        
        if len(self.members) != len(other.members):
            return False
        
        matched = []
        for cluster1 in self.members :
            for cluster2 in other.members :
                if cluster1.equivalent(cluster2) and cluster2 not in matched:
                    matched.append(cluster2)
        return len(matched) == len(self.members)
    
    
    #============================================================
    # manipulation
    #============================================================

    def add(self, cluster):
        """
        Add cluster to this cluster set (only if it does not already exist).
        
        If the cluster is already in this cluster set, raise a ValueError.
        
        Parameters
        --------------------
            cluster -- Cluster, cluster to add
        """
        
        if cluster in self.members :
            raise ValueError
        
        self.members.append(cluster)

"""## k-means and k-medoids algorithms"""

######################################################################
# k-means and k-medoids
######################################################################

def random_init(points, k) :
    """
    Randomly select k unique elements from points to be initial cluster centers.
    
    Parameters
    --------------------
        points         -- list of Points, dataset
        k              -- int, number of clusters
    
    Returns
    --------------------
        initial_points -- list of k Points, initial cluster centers
    """

    return np.random.choice(points, size = k, replace = False)



def cheat_init(points) :
    """
    Initialize clusters by cheating!
    
    Details
    - Let k be number of unique labels in dataset.
    - Group points into k clusters based on label (i.e. class) information.
    - Return medoid of each cluster as initial centers.
    
    Parameters
    --------------------
        points         -- list of Points, dataset
    
    Returns
    --------------------
        initial_points -- list of k Points, initial cluster centers
    """

    initial_points = []
    labels = []
    for point in points:
      labels.append(point.label)
    group = {}
    for label in labels:
      group[label] = []
    for point in points:
      group[point.label].append(point)
    clusters = []
    for i, j in group.items():
      cluster = Cluster(j)
      clusters.append(cluster)
    initial_points = [cluster.medoid() for cluster in clusters]
    return initial_points


def kAverage(points, k, average, init='random', plot=True):
    count = 1
    if init == 'random':
        mu = random_init(points, k)
    elif init == 'cheat':
        mu = cheat_init(points)
    
    k_clusters = ClusterSet()

    while True:
        clusters = {}
        for mu1 in mu:
          clusters[mu1] = Cluster([])
        for point in points: 
            distances = [point.distance(mu1) for mu1 in mu]
            index = np.argmin(distances)
            #closest_mu = mu[index]
            clusters[mu[index]].points.append(point)
        new_clusters = ClusterSet()
        for mu1, cluster in clusters.items():
            new_clusters.add(cluster)

        if (k_clusters.equivalent(new_clusters)) and len(k_clusters.members) > 0:
            if average == ClusterSet.centroids:
                name = "k-means"
            else:
                name = "k-medoids"
            print(f"{name} STOPPED AT ITERATION:{count}")
            break
        mu = average(new_clusters)
        k_clusters = new_clusters
        
        if plot == True:
            if average == ClusterSet.centroids:
                plot_clusters(new_clusters, f"k-means k={k} count={count}", average)
            else:
                plot_clusters(new_clusters, f"k-medoids k={k} count={count}", average)
        count += 1

    return k_clusters



def kMeans(points, k, init='random', plot=False) :
    """
    Cluster points into k clusters using variations of k-means algorithm.
    
    Parameters
    --------------------
        points  -- list of Points, dataset
        k       -- int, number of clusters
        average -- method of ClusterSet
                   determines how to calculate average of points in cluster
                   allowable: ClusterSet.centroids, ClusterSet.medoids
        init    -- string, method of initialization
                   allowable: 
                       'cheat'  -- use cheat_init to initialize clusters
                       'random' -- use random_init to initialize clusters
        plot    -- bool, True to plot clusters with corresponding averages
                         for each iteration of algorithm
    
    Returns
    --------------------
        k_clusters -- ClusterSet, k clusters
    """

    return kAverage(points, k, ClusterSet.centroids, init=init, plot=plot)



def kMedoids(points, k, init='random', plot=False) :
    """
    Cluster points in k clusters using k-medoids clustering.
    See kMeans(...).
    """

    
    return kAverage(points, k, ClusterSet.medoids, init=init, plot=plot)


"""## Utilities"""

######################################################################
# helper functions
######################################################################

def build_face_image_points(X, y) :
    """
    Translate images to (labeled) points.
    
    Parameters
    --------------------
        X     -- numpy array of shape (n,d), features (each row is one image)
        y     -- numpy array of shape (n,), targets
    
    Returns
    --------------------
        point -- list of Points, dataset (one point for each image)
    """
    
    n,d = X.shape
    
    images = collections.defaultdict(list) # key = class, val = list of images with this class
    for i in range(n) :
        images[y[i]].append(X[i,:])
    
    points = []
    for face in images :
        count = 0
        for im in images[face] :
            points.append(Point(str(face) + '_' + str(count), face, im))
            count += 1

    return points


def plot_clusters(clusters, title, average) :
    """
    Plot clusters along with average points of each cluster.

    Parameters
    --------------------
        clusters -- ClusterSet, clusters to plot
        title    -- string, plot title
        average  -- method of ClusterSet
                    determines how to calculate average of points in cluster
                    allowable: ClusterSet.centroids, ClusterSet.medoids
    """
    
    plt.figure()
    np.random.seed(20)
    label = 0
    colors = {}
    centroids = average(clusters)
    for c in centroids :
        coord = c.attrs
        plt.plot(coord[0],coord[1], 'ok', markersize=12)
    for cluster in clusters.members :
        label += 1
        colors[label] = np.random.rand(3,)
        for point in cluster.points :
            coord = point.attrs
            plt.plot(coord[0], coord[1], 'o', color=colors[label])
    plt.title(title)
    plt.show()


def generate_points_2d(N, seed=1234) :
    """
    Generate toy dataset of 3 clusters each with N points.
    
    Parameters
    --------------------
        N      -- int, number of points to generate per cluster
        seed   -- random seed
    
    Returns
    --------------------
        points -- list of Points, dataset
    """
    np.random.seed(seed)
    
    mu = [[0,0.5], [1,1], [2,0.5]]
    sigma = [[0.1,0.1], [0.25,0.25], [0.15,0.15]]
    
    label = 0
    points = []
    for m,s in zip(mu, sigma) :
        label += 1
        for i in range(N) :
            x = random_sample_2d(m, s)
            points.append(Point(str(label)+'_'+str(i), label, x))
    
    return points

"""## Main function"""

######################################################################
# main
######################################################################

def main() :
    #explore LFW data set
    X, y = get_lfw_data()
    show_image(X[2])
    show_image(X[4])
    show_image(X[6])
    mean = np.mean(X, axis = 0)
    show_image(mean)

    U, mu= util.PCA(X)
    plot_gallery([vec_to_image(U[:,i]) for i in range(12)]) 

    l_components = [1, 10, 50, 100, 500, 1288]
    plot_gallery(X[:12], title = '12 original images' )
    for l in l_components:
      Y, U1 = apply_PCA_from_Eig(X, U, l, mu)
      rec = reconstruct_from_PCA(Y, U1, mu)
      print(l)
      plot_gallery(rec[:12], title = '12 new images')

    # cluster toy dataset
    np.random.seed(1234)
    toy_dataset = generate_points_2d(20)
    kMeans(toy_dataset, 3, init = 'random', plot = True)
    kMedoids(toy_dataset, 3, init = 'random', plot = True)
    kMeans(toy_dataset, 3, init = 'cheat', plot = True)
    kMedoids(toy_dataset, 3, init = 'cheat', plot = True)

    np.random.seed(1234)
    X1, y1 = util.limit_pics(X, y, [4, 6, 13, 16], 40)
    points = build_face_image_points(X1, y1)
    k_means = []
    k_medoids = []
    for i in range (10):
      k_means.append(kMeans(points, 4, init = 'random').score())
      k_medoids.append(kMedoids(points, 4, init = 'random').score())
    print("k_means sum", sum(k_means),"min ",min(k_means),"max ",max(k_means))
    print("k_medoids sum", sum(k_medoids),"min ",min(k_medoids),"max ",max(k_medoids))


        
    #explore effect of lower-dimensional representations on clustering performance
    np.random.seed(1234)
    U, mu = util.PCA(X)
    X1, y1 = util.limit_pics(X, y, [4, 13], 40)
    principal = np.arange(1, 42, 2)
    k_means = []
    k_medoids = []

    for l in principal:
      Y, U1 = apply_PCA_from_Eig(X1, U, l, mu)
      rec = reconstruct_from_PCA(Y, U1, mu)
      points = build_face_image_points(rec, y1)
      cluster1 = kMeans(points, 2, init = 'cheat') 
      k_means.append(cluster1.score())
      cluster2 = kMedoids(points, 2, init = 'cheat')
      k_medoids.append(cluster2.score())

    plt.figure()
    plt.plot(principal, k_means, color = 'red', label = 'k-means')
    plt.plot(principal, k_medoids, color = 'blue', label = 'k-medoids')
    plt.ylabel('Clustering Score')
    plt.xlabel('Number of Components')
    plt.legend()
    plt.show()

    
    # determine ``most discriminative'' and ``least discriminative'' pairs of images
    np.random.seed(1234)
    sets = set(y)
    number = len(sets)
    Min = 99999
    Max = 0
    min_pair, max_pair = [0, 0]

    for i in range(number):
      for j in range(number):
        if i != j:
          X1, y1 = util.limit_pics(X, y, [i, j], 40)
          points = build_face_image_points(X1, y1)
          cluster = kMeans(points, 2, init = 'cheat')
          if cluster.score() < Min:
            Min = cluster.score()
            min_pair = [i, j]
          if cluster.score() > Max:
            Max = cluster.score()
            max_pair = [i, j]

    print(min_pair, max_pair)

    plt.figure ()
    for i in range(len(min_pair)):
        plt.subplot (1,len(min_pair),i+1)
        label = min_pair[i]
        plt.imshow (get_rep_image (X, y, label), cmap = plt.cm.gray)
        plt.axis ('off')
    plt.show ()

    for i in range(len(max_pair)):
        plt.subplot (1,len(max_pair),i+1)
        label = max_pair[i]
        plt.imshow (get_rep_image (X, y, label), cmap = plt.cm.gray)
        plt.axis ('off')
    plt.show ()
    
    ### ========== TODO : END ========== ###


if __name__ == "__main__" :
    main()

