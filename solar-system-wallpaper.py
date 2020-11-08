import solarsystem
import datetime
import os
import ctypes
from math import sqrt, cos, sin, acos, pi, radians, degrees, ceil, copysign
from PIL import Image, ImageDraw
from random import randint

# Opening the base wallpaper
bg = Image.open("images/fond.png").convert('RGBA')

# Creating the transparent overlays
stars_overlay = Image.new('RGBA', bg.size, (0, 0, 0, 0))
planets_overlay = Image.new('RGBA', bg.size, (0, 0, 0 ,0))
asteroids_overlay = Image.new('RGBA', bg.size, (0, 0, 0, 0))

# Dictionary with the sizes and rays of the planets
planets_size = {

    "Mercury" : ((5, 5), 2),
    "Venus" : ((13, 13), 6),
    "Earth" : ((13, 13), 6),
    "Mars" : ((11, 11), 5),
    "Jupiter" : ((25, 25), 12),
    "Saturn" : ((25, 25), 12),
    "Uranus" : ((17, 17), 8),
    "Neptune" : ((15, 15), 7),
    "Moon" : ((5, 5), 2)
}

# Dictionary with the radius of the orbit of the planets
planets_radius = {

    "Mercury" : 49.5,
    "Venus" : 70.5,
    "Earth" : 102,
    "Mars" : 134.5,
    "Jupiter" : 241,
    "Saturn" : 312,
    "Uranus" : 369,
    "Neptune" : 447,
    "Moon" : 23
}

# Dictionary with image references of the planets
planets_image = {
    
    "Mercury" : Image.open("images/mercure.png"),
    "Venus" : Image.open("images/venus.png"),
    "Earth" : Image.open("images/terre.png"),
    "Mars" : Image.open("images/mars.png"),
    "Jupiter" : Image.open("images/jupiter.png"),
    "Saturn" : Image.open("images/saturne.png"),
    "Uranus" : Image.open("images/uranus.png"),
    "Neptune" : Image.open("images/neptune.png"),
    "Moon" : Image.open("images/lune.png")
}

#
# Stars generation
#

nbr_big_stars = 30
nbr_small_stars = 100

# Generating big stars
for i in range(nbr_big_stars):

    # Creating a circle and resizing it to a random size
    star_image = Image.new('RGBA', (40, 40), (0, 0, 0 ,0))

    draw = ImageDraw.Draw(star_image)
    draw.ellipse((0,0,39,39), fill=(255, 255, 255, 220))

    x_star = randint(3, 4)
    y_star = randint(3, 4)

    resized_star = star_image.resize((x_star, y_star))

    # Getting a random position
    x, y = randint(0, 1915), randint(0, 1075)

    # Pasting the star at this position
    stars_overlay.paste(resized_star, (x, y))

# Generating small stars
for i in range(nbr_small_stars):

    # Creating a circle and resizing it ot a random size
    star_image = Image.new('RGBA', (40, 40), (0, 0, 0 ,0))

    draw = ImageDraw.Draw(star_image)
    draw.ellipse((0,0,39,39), fill=(255, 255, 255, 220))

    x_star = randint(0, 1)

    y_star = 1 - x_star + 1
    x_star = x_star + 1

    resized_star = star_image.resize((x_star, y_star))

    # Getting a random position
    x, y = randint(0, 1918), randint(0, 1078)

    # Pasting the star at this position
    stars_overlay.paste(resized_star, (x, y))

bg = Image.alpha_composite(bg, stars_overlay)

#
# Asteroids generation
#

nbr_asteroids = randint(120, 160)

compt_aster = 0

while(compt_aster <= nbr_asteroids):

    x_aster = randint(-221, 221)
    y_aster = randint(-221, 221)

    radius = sqrt(x_aster**2 + y_aster**2)

    if(radius > 221 or radius < 146):
        continue
    
    compt_aster += 1

    x_aster_img = 2
    y_aster_img = x_aster_img + randint(-1, 1)

    if(randint(0, 1)):
        y_aster_img, x_aster_img = x_aster_img, y_aster_img

    asteroid_image = Image.new('RGBA', (40, 40), (0, 0, 0 ,0))

    draw = ImageDraw.Draw(asteroid_image)
    draw.ellipse((0,0,39,39), fill=(208, 182, 150, 128))

    resize_asteroid = asteroid_image.resize((x_aster_img, y_aster_img))

    asteroids_overlay.paste(resize_asteroid, (x_aster + 960, y_aster + 540))
    
bg = Image.alpha_composite(bg, asteroids_overlay) 

#
# Planets positioning
#

# Getting the current time
now = datetime.datetime.utcnow()
year   = now.year
month  = now.month
day    = now.day
hour   = now.hour
minute = now.minute

# Getting the current positions of the planets
H = solarsystem.Heliocentric(year=year, month=month, day=day, hour=hour, minute=minute, view='rectangular')
planets = H.planets()

# Deleting useless plane
del planets["Pluto"]
del planets["Ceres"]
del planets["Chiron"]
del planets["Eris"]

for planet_name in planets:
    

    # Getting the position of the planet
    pos = planets[planet_name]
    x = pos[0]
    y = pos[1]
    
    norm = sqrt(x**2 + y**2)

    # Getting the angle between the planet, the sun and a horizontal axis
    # Adding pi/2 to compensate for the initial orientation of the images of the planets
    planet_angle = acos(x/norm) + pi/2

    if(y < 0):
        planet_angle = pi - planet_angle

    # Getting the image of the planet
    planet_image = planets_image[planet_name]

    # Rotating to align the shadow and resizing it
    rotated_planet = planet_image.rotate(degrees(planet_angle))
    resized_planet = rotated_planet.resize(planets_size[planet_name][0]).convert('RGBA')

    # Getting the top right position of the planet
    planet_center = (ceil(planets_radius[planet_name]*cos(planet_angle - pi/2)) + 960 - planets_size[planet_name][1],
                     -ceil(planets_radius[planet_name]*sin(planet_angle - pi/2)) + 540 - planets_size[planet_name][1])

    # Adding the planet to the transparent overlay
    planets_overlay.paste(resized_planet, planet_center)

    # Adding the Moon
    if(planet_name == "Earth"):

        # Getting the position of the Moon around the Earth
        pos_moon = solarsystem.Moon(year=year, month=month, day=day, hour=hour, minute=minute, longtitude=0.0, latitude=0.0).position()

        # Getting the position of the Sun around the Earth
        pos_sun = solarsystem.Geocentric(year=year, month=month, day=day, hour=hour, minute=minute, plane='equatorial').position()["Sun"]

        # Getting the angle between the Sun and the Moon
        moon_angle = -radians(pos_sun[0] - pos_moon[0])

        # Getting the normalized vector bewteen the Sun and the Moon to the distance bewteen the Earth and the Moon
        earth_sun_vect = (0 - x, 0 - y)

        norm = sqrt(earth_sun_vect[0]**2 + earth_sun_vect[1]**2)

        earth_sun_vect_normed = tuple(planets_radius["Moon"]*x/norm for x in earth_sun_vect)

        # Rotating the previous vector to get the vector bewteen the Earth and the Moon 
        earth_moon_vect = (cos(moon_angle)*earth_sun_vect_normed[0] - sin(moon_angle)*earth_sun_vect_normed[1], sin(moon_angle)*earth_sun_vect_normed[0] + cos(moon_angle)*earth_sun_vect_normed[1])

        # Getting and rotating the image of the Moon
        rotated_moon = planets_image["Moon"].rotate(degrees(planet_angle))

        # Resizing the image
        resized_moon = rotated_moon.resize(planets_size["Moon"][0]).convert('RGBA')

        # Getting the top right position of the planet
        moon_center = (ceil(planet_center[0] + planets_size[planet_name][1] + earth_moon_vect[0]) - planets_size["Moon"][1], ceil(planet_center[1] + planets_size[planet_name][1] - earth_moon_vect[1]) - planets_size["Moon"][1])

        # Adding the Moon to the transparent overlay
        planets_overlay.paste(resized_moon, moon_center)

# Merging the planets overlay to the wallpaper and saving it
bg = Image.alpha_composite(bg, planets_overlay)
bg.save("wallapaper.png")

# Setting the wallpaper as teh destop background
path = os.getcwd() + '\\wallapaper.png'
ctypes.windll.user32.SystemParametersInfoW(20,0,path,0)

'''
#print(cos(angles["Mercury"]))

M = solarsystem.Moon(year=2020, month=11, day=5, hour=20, minute=53, longtitude=0.0, latitude=0.0)

T = solarsystem.Geocentric(year=2020, month=11, day=5, hour=20, minute=53, plane='equatorial')

#print(T.position()["Sun"])

angle = -radians(T.position()["Sun"][0] - M.position()[0])
#print(angle)

vect = (0 - planets["Earth"][0], 0 - planets["Earth"][1])

norm = sqrt(vect[0]**2 + vect[1]**2)

new_vect = tuple(moon_radius*x/norm for x in vect)

new_vect2 = (cos(angle)*new_vect[0] - sin(angle)*new_vect[1], sin(angle)*new_vect[0] + cos(angle)*new_vect[1])

Lune = (planets["Earth"][0] + new_vect2[0], planets["Earth"][1] + new_vect2[1])
'''
'''plt.scatter(0, 0, color='yellow')
plt.scatter(planets["Earth"][0], planets["Earth"][1], color='blue')
plt.scatter(Lune[0], Lune[1], color='red')'''
'''
rotated_mercure = mercure.rotate(degrees(angles["Mercury"]))

#int(2*cos(angles["Mercury"] + pi/2)/abs(cos(angles["Mercury"] + pi/2))
# + int(2*sin(angles["Mercury"] + pi/2)/abs(cos(angles["Mercury"] + pi/2)))
mercury_center = (ceil(mercure_radius*cos(angles["Mercury"] - pi/2)) + 960 + int(copysign(2, cos(angles["Mercury"] - pi/2))), - ceil(mercure_radius*sin(angles["Mercury"] - pi/2)) + 540 - int(copysign(2, sin(angles["Mercury"] - pi/2))))

print(ceil(cos(angles["Mercury"] - pi/2)*49) + 960)

resize_mercure = rotated_mercure.resize((5, 5)).convert('RGBA')

overlay = Image.new('RGBA', bg.size, (0, 0, 0 ,0))
overlay.paste(resize_mercure, mercury_center)

bg = Image.alpha_composite(bg, overlay)

bg.save("oui.png")

#plt.show()'''
