import math

class Vector3d:
	
	def __init__(self, xyz):
		self.x, self.y, self.z = xyx
	
	
class Point3d:
	
	def __init__(self, xyz):
		self.x, self.y, self.z = xyz
		
	def add_vect(self, vect):
		return Point3d((self.x + vect.x, self.y + vect.y, self.z + vect.z))
	
	def translate(self, xyz):
		return Point3d((self.x + xyz[0], self.y + xyz[1], self.z + xyz[2]))
	
	def rotate_x(self, theta):
		cos = math.cos(theta)
		sin = math.sin(theta)
		return Point3d((self.x, self.y * cos - self.z * sin, self.y * sin + self.z * cos))
	
	def rotate_z(self, theta):
		cos = math.cos(theta)
		sin = math.sin(theta)
		return Point3d((self.x * cos - self.y * sin, self.y * cos + self.x * sin, self.z))
	
	def rotate_y(self, theta):
		cos = math.cos(theta)
		sin = math.sin(theta)
		return Point3d((self.x * cos + self.z * sin, self.y, self.z * cos - self.x * sin))
	
	def scale(self, xyz):
		return Point3d((self.x * xyz[0], self.y * xyz[1], self.z * xyz[2]))
	
	def __str__(self):
		return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")" 

def calc_distance(triangle, 
	
point = Point3d((1, 2, 1))
print point.rotate_y(math.radians(45))
print point.rotate_y(math.radians(60)).rotate_y(math.radians(60))
print point.rotate_y(math.radians(60)).rotate_y(math.radians(60)).rotate_y(math.radians(60))
print point.scale((3, 0.5, 1))
