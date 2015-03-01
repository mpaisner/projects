'''
Assumptions: 
	1) Variance is only read when people in a pop segment are added to or removed from a skill (including when populations are updated). For the purpose of using skills, skill level is considered to be constant. 
	2) Skill is considered to be normally distributed within a segment. This means that adding low-skill workers for a short time, then removing them, will adversely effect overall skill level. This is not totally unrealistic, and anyway is a necessary assumption unless I think of something better.
'''

#Eventually, it will be necessary to fix variances. the variance of a sub-distribution away from the center should be less than the variance of the main distribution, so it can fit inside it. However, I'm not exactly sure how to calculate this.
class SkillProfile:
	
	def __init__(self, num, skill, mean, variance):
		self.num = num
		self.skill = skill
		self.mean = mean
		self.variance = variance
	
	def __str__(self):
		return str(self.num) + " people with skill " + str(round(self.mean, 1)) + "(" + str(round(self.variance, 1)) + ") at " + self.skill.name
	
	def combined_mean(self, prof1, prof2):
		if prof1.num + prof2.num == 0:
			return 0.0
		return (prof1.mean * prof1.num + prof2.mean * prof2.num) / (prof1.num + prof2.num)
	
	def combined_variance(self, prof1, prof2, mean = None):
		if prof1.num + prof2.num == 0:
			return 0.0
		if not mean:
			mean = self.combined_mean(prof1, prof2)
		return ((prof1.num * (prof1.mean ** 2 + prof1.variance) + prof2.num * (prof2.mean ** 2 + prof2.variance)) / (prof1.num + prof2.num)) - mean ** 2
	
	def copy_profile(self, prof):
		self.skill = prof.skill
		self.num = prof.num
		self.mean = prof.mean
		self.variance = prof.variance
	
	def copy(self):
		return SkillProfile(self.num, self.skill, self.mean, self.variance)
	
	def combine_profiles(self, prof1, prof2):
		if prof2.skill != prof1.skill:
			prof2.change_skill(prof1.skill)
		mean = self.combined_mean(prof1, prof2)
		variance = self.combined_variance(prof1, prof2, mean)
		return SkillProfile(prof1.num + prof2.num, prof1.skill, mean, variance)
	
	def add_workers(self, profile):
		self.copy_profile(self.combine_profiles(self, profile))
	
	def subtract_profiles(self, prof1, prof2):
		num = prof1.num - prof2.num
		if num > 0:
			mean = (prof1.mean * prof1.num - prof2.mean * prof2.num) / num
			variance = ((prof1.variance + prof1.mean ** 2) * prof1.num - prof2.num * (prof2.variance + prof2.mean ** 2)) / num - mean ** 2
		else:
			mean = 0
			variance = 0
		return SkillProfile(num, prof1.skill, mean, variance)
	
	def remove_workers(self, profile):
		self.copy_profile(self.subtract_profiles(self, profile))
	
	#returns the z value necessary to get num/2 people in the tail of the curve (so a mean can be at that z value)
	def num_in_tail_to_z(self, num):
		fraction = float(num) / self.num
		return fraction_to_z(fraction)
	
	def num_to_max_dist_from_mean(self, num):
		fraction = float(num) / self.num / 2
		return self.z_to_distance_from_mean(fraction_to_z(fraction))
	
	def z_to_distance_from_mean(self, z):
		sd = self.variance ** 0.5
		return sd * z
	
	def val_to_fraction_in_tail(self, val):
		sd = self.variance ** 0.5
		z = abs(val - self.mean) / sd
		return z_to_fraction(z)
	
	def num_in_interval(self, start, end):
		if start > end:
			raise ValueError("start of interval must be <= end")
		if start < self.mean and end < self.mean:
			fraction = self.val_to_fraction_in_tail(end) - self.val_to_fraction_in_tail(start)
		elif start < self.mean and end >= self.mean:
			fraction = 1 - self.val_to_fraction_in_tail(start) - self.val_to_fraction_in_tail(end)
		else: #both are >= mean
			fraction = self.val_to_fraction_in_tail(start) - self.val_to_fraction_in_tail(end)
		return fraction * self.num
	
	def can_remove(self, prof):
		try:
			return self.num >= prof.num >= 0 and prof.num == int(prof.num) and abs(prof.mean - self.mean) <= self.num_to_max_dist_from_mean(prof.num)
		except ValueError:
			return False
	
	def get_worst_workers(self, num):
		if num >= self.num:
			return SkillProfile(self.num, self.skill, self.mean, self.variance)
		elif num == 0:
			return SkillProfile(0, self.skill, self.mean, self.variance)
		elif num != int(num):
			raise ValueError("Only whole numbers of people can be moved. We're not barbarians.")
		mean = self.mean - self.z_to_distance_from_mean(self.num_in_tail_to_z(float(num) / 2))
		variance = self.variance
		return SkillProfile(num, self.skill, mean, variance)
	
	def get_best_workers(self, num):
		ret = self.get_worst_workers(num)
		ret.mean = 2 * self.mean - ret.mean
		return ret
	
	#may not return a legal segment; check with can_remove()
	def workers_with_mean(self, num, mean):
		if num < 0:
			num = 0
		elif num > self.num:
			num = self.num
		elif num != int(num):
			raise ValueError("Only whole numbers of people can be moved. We're not barbarians.")
		return SkillProfile(num, self.skill, mean, self.variance)
	
	#this will ultimately consult a table.
	def change_skill(self, skill):
		self.mean *= 0.67
		self.variance *= 0.67 ** 2
		self.skill = skill

class SkillProfile:
	
	def __init__(self, num, skill, mean):
		self.num = num
		self.skill = skill
		self.mean = mean
	
	def variance(self):
		return self.mean * self.skill.percentvariance
	
	def __str__(self):
		return str(self.num) + " people with skill " + str(round(self.mean, 1)) + " at " + self.skill.name
	
	def combined_mean(self, prof1, prof2):
		if prof1.num + prof2.num == 0:
			return 0.0
		return (prof1.mean * prof1.num + prof2.mean * prof2.num) / (prof1.num + prof2.num)
	
	def copy_profile(self, prof):
		self.skill = prof.skill
		self.num = prof.num
		self.mean = prof.mean
	
	def copy(self):
		return SkillProfile(self.num, self.skill, self.mean)
	
	def combine_profiles(self, prof1, prof2):
		if prof2.skill != prof1.skill:
			prof2.change_skill(prof1.skill)
		mean = self.combined_mean(prof1, prof2)
		return SkillProfile(prof1.num + prof2.num, prof1.skill, mean)
	
	def add_workers(self, profile):
		self.copy_profile(self.combine_profiles(self, profile))
	
	def subtract_profiles(self, prof1, prof2):
		num = prof1.num - prof2.num
		if num > 0:
			mean = (prof1.mean * prof1.num - prof2.mean * prof2.num) / num
		else:
			mean = 0
		return SkillProfile(num, prof1.skill, mean)
	
	def remove_workers(self, profile):
		self.copy_profile(self.subtract_profiles(self, profile))
	
	#returns the z value necessary to get num/2 people in the tail of the curve (so a mean can be at that z value)
	def num_in_tail_to_z(self, num):
		fraction = float(num) / self.num
		return fraction_to_z(fraction)
	
	def num_to_max_dist_from_mean(self, num):
		fraction = float(num) / self.num / 2
		return self.z_to_distance_from_mean(fraction_to_z(fraction))
	
	def z_to_distance_from_mean(self, z):
		sd = self.variance() ** 0.5
		return sd * z
	
	def val_to_fraction_in_tail(self, val):
		sd = self.variance() ** 0.5
		z = abs(val - self.mean) / sd
		return z_to_fraction(z)
	
	def num_in_interval(self, start, end):
		if start > end:
			raise ValueError("start of interval must be <= end")
		if start < self.mean and end < self.mean:
			fraction = self.val_to_fraction_in_tail(end) - self.val_to_fraction_in_tail(start)
		elif start < self.mean and end >= self.mean:
			fraction = 1 - self.val_to_fraction_in_tail(start) - self.val_to_fraction_in_tail(end)
		else: #both are >= mean
			fraction = self.val_to_fraction_in_tail(start) - self.val_to_fraction_in_tail(end)
		return fraction * self.num
	
	def can_remove(self, prof):
		try:
			return self.num >= prof.num >= 0 and prof.num == int(prof.num) and abs(prof.mean - self.mean) <= self.num_to_max_dist_from_mean(prof.num)
		except ValueError:
			return False
	
	def get_worst_workers(self, num):
		if num >= self.num:
			return SkillProfile(self.num, self.skill, self.mean)
		elif num == 0:
			return SkillProfile(0, self.skill, self.mean)
		elif num != int(num):
			raise ValueError("Only whole numbers of people can be moved. We're not barbarians.")
		mean = self.mean - self.z_to_distance_from_mean(self.num_in_tail_to_z(float(num) / 2))
		return SkillProfile(num, self.skill, mean)
	
	def get_best_workers(self, num):
		ret = self.get_worst_workers(num)
		ret.mean = 2 * self.mean - ret.mean
		return ret
	
	#may not return a legal segment; check with can_remove()
	def workers_with_mean(self, num, mean):
		if num < 0:
			num = 0
		elif num > self.num:
			num = self.num
		elif num != int(num):
			raise ValueError("Only whole numbers of people can be moved. We're not barbarians.")
		return SkillProfile(num, self.skill, mean, self.variance)
	
	#this will ultimately consult a table.
	def change_skill(self, skill):
		self.mean *= 0.67
		self.skill = skill

def test_sp():
	archery = Skill("hunting", "hunting", lambda oldskl, employper, dtime: oldskl + 0.5 * employper * dtime, lambda oldskl, age, dtime: oldskl - max(0, (age - 30) / 300), 0.3)
	prof1 = SkillProfile(20, archery, 8.0)
	print prof1.variance()
	worst = prof1.get_worst_workers(7)
	print worst.mean, worst.variance()
	best = prof1.get_best_workers(7)
	print best.mean, best.variance()
	print prof1.num_in_interval(best.mean, 15)
	print prof1.num_in_interval(1, best.mean)
	prof1.remove_workers(worst)
	print prof1.mean, prof1.variance(), prof1.num
	nextworst = prof1.get_worst_workers(6)
	print nextworst.mean
	prof1.remove_workers(nextworst)
	print prof1.mean, prof1.variance(), prof1.num
	sys
	prof1.add_workers(worst)
	print prof1.mean, prof1.variance, prof1.num
	print worst.mean, worst.variance, worst.num
	print prof1.num_in_interval(1, 5.75)
	print prof1.num_in_interval(1, 7.8)
	print prof1.num_to_max_dist_from_mean(2)
	print prof1.can_remove(prof1)
	prof2.copy_profile(prof1)
	prof2.mean = 6.9
	prof2.num = 8
	print prof1.can_remove(prof2)
	prof1.remove_workers(prof2)
	print prof1.mean, prof1.variance, prof1.num
	
test_sp()

class SkillProfile:
	
	numsegments = 100
	
	def __init__(self, skill):
		self.skill = skill
		self.segments = [0 for i in range(self.numsegments)]
	
	def change_skill(self, skill):
		multiplier = 0.67 #read from table
		newsegments = [0 for i in range(self.numsegments)]
		for i in range(self.numsegments):
			newworkers[min(numsegments - 1, int(round(multiplier * i, 0)))] += self.segments[i]
		self.segments = newsegments
	
	def __getitem__(self, item):
		if isinstance(item, slice):
			return [0 for i in range(item.start)] + self.segments[item.start:item.stop] + [0 for i in range(self.numsegments - item.stop)]
		else:
			return self.segments[item]
	
	def num_in_interval(self, start, end):
		return sum(self[start:end])
	
	def copy(self):
		cpy = SkillProfile(self.skill)
		cpy.segments = list(self.segments)
	
	def add_workers(self, prof1, prof2):
		if prof2.skill != prof1.skill:
			prof2.change_skill(prof1.skill)
		for i in range(self.numsegments):
			prof1.segments[i] += prof2.segments[i]
	
	def remove_workers(self, profile):
		for i in range(self.numsegments):
			prof1.segments[i] -= prof2.segments[i]
			if prof1.segments[i] < 0:
				raise ValueError("Too many workers removed")