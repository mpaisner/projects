import random, math

class Vector:
	
	def __init__(self, v):	
		self.vector = v
	
	def __getitem__(self, item):
		return self.vector[item]
	
	def __len__(self):
		return len(self.vector)
	
	def __str__(self):
		return str(self.vector)

def vectorize(list):
	newlist = []
	for v in list:
		newlist.append(Vector(v))
	return newlist

def unvectorize(list):
	newlist = []
	for vector in list:
		newlist.append(vector.vector)
	return newlist

def distance(one, two):
	if hasattr(one, "loc"):
		if hasattr(two, "loc"):
			return distance(one.loc, two.loc)
		else:
			return distance(one.loc, two)
	if hasattr(two, "loc"):
		return distance(one, two.loc)
	assert len(one) == len(two)
	dist = 0
	for i in range(len(one)):
		dist += (one[i] - two[i]) ** 2
	return math.sqrt(dist)

#select next centroid that is farthest from current centroids (sum of distances)
def select_centroid(centroids, vectors):
	maxdist = -1
	vect = None
	for vector in vectors:
		dist = 0
		for centroid in centroids:
			dist += distance(centroid, vector)
		if dist > maxdist:
			maxdist = dist
			vect = vector
	return vect

def select_start_centroids(k, vectors):
	centroids = []
	vectors = vectors[:]
	centroids.append(random.choice(vectors))
	vectors.remove(centroids[-1])
	
	while len(centroids) < k and vectors:
		centroids.append(select_centroid(centroids, vectors))
		vectors.remove(centroids[-1])
	return centroids

def assign_to_centroids(centroids, vectors):
	assignments = {}
	for vector in vectors:
		mindist = float("inf")
		closest = None
		for centroid in centroids:
			dist = distance(vector, centroid)
			if dist < mindist:
				mindist = dist
				closest = centroid
		assignments[vector] = closest
	return assignments

def add(v1, v2):
	assert len(v1) == len(v2)
	newv = []
	for i in range(len(v1)):
		newv.append(v1[i] + v2[i])
	return newv

def divide(v, scalar):
	return [1.0 * val / scalar for val in v]

def calc_new_centroids(centroids, assignments):
	newcentroids = {}
	for centroid in centroids:
		newcentroids[centroid] = ([0 for i in range(len(centroid))], 0)
	for vector, centroid in assignments.items():
		newcentroids[centroid] = (add(newcentroids[centroid][0], vector), newcentroids[centroid][1] + 1)
	ret = []
	for old, new in newcentroids.items():
		if new[1] == 0:
			ret.append(old)
		else:
			ret.append(divide(new[0], new[1]))
	return vectorize(ret)

def centroids_changed(lastcentroids, currentcentroids, mindist = 0.0001):
	if not lastcentroids:
		return True
	for centroid1 in lastcentroids:
		found = False
		for centroid2 in currentcentroids:
			if distance(centroid1, centroid2) < mindist:
				found = True
				break
		if not found:
			return True
	return False

def get_final_centroids(k, vectors, maxiterations):
	centroids = select_start_centroids(k, vectors)
	lastcentroids = None
	iterations = 0
	while centroids_changed(lastcentroids, centroids) and iterations < maxiterations:
		newcentroids = calc_new_centroids(centroids, assign_to_centroids(centroids, vectors))
		lastcentroids = centroids
		centroids = newcentroids
		iterations += 1
	return centroids, iterations

def get_clusters(centroids, vectors):
	assignments = assign_to_centroids(centroids, vectors)
	clusters = {}
	for vector, centroid in assignments.items():
		if centroid in clusters:
			clusters[centroid].append(vector)
		else:
			clusters[centroid] = [vector]
	return clusters

def k_means(k, vectors, maxiterations = 100):
	centroids, iterations = get_final_centroids(k, vectors, maxiterations)
	return get_clusters(centroids, vectors), iterations

def mean_dist(clusters):
	if not clusters:
		return 0
	dist = 0
	for centroid, vectors in clusters.items():
		for vector in vectors:
			dist += distance(vector, centroid)
	return dist / sum([len(assignment) for assignment in clusters.values()])

def best_k_means(vectors, clusterfactor = 0.5, maxk = 10, maxiterations = 100, maxconsecutiveincrease = 2):
	results = []
	for k in range(1, maxk + 1):
		print k
		clusters = k_means(k, vectors, maxiterations = maxiterations)[0]
		meandist = mean_dist(clusters)
		results.append((k, meandist * (k ** clusterfactor), clusters))
		if len(results) > maxconsecutiveincrease:
			increasing = True
			for i in range(-maxconsecutiveincrease - 1, -1):
				if results[i][1] > results[i + 1][1]:
					increasing = False
					break
			if increasing:
				break
	minerror = float("inf")
	best = None
	for k, error, clusters in results:
		if error < minerror:
			minerror = error
			best = clusters
	return best

#####
##Testing
#####

def rand_vect(means, devs):
	vect = []
	for mean, dev in zip(means, devs):
		vect.append(mean + (random.random() - 0.5) * dev)
	return vect

if __name__ == "__main__":
	data = [rand_vect([0,1,2], [0.5, 0.2, 0.3]) for i in range(500)]
	data += [rand_vect([2,1,2], [0.5, 0.2, 0.3]) for i in range(500)]
	vectors = vectorize(data)
	random.shuffle(data)
	
	clusters = best_k_means(vectors)
	for cluster in clusters:
		print cluster, ":", len(unvectorize(clusters[cluster]))
	print mean_dist(clusters)
