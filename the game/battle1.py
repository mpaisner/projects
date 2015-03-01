from Tkinter import *

'''
*) enemys can always see units that have been committed or that have bombarded. By default, they cannot see units held in reserve that have not bombarded.

*) units can have 'bombardment' style ranged attacks which are used from reserve, or they can have 'first strike' bombardment attacks which enhance their first turn entering melee and/or give them a first strike ability.

*) odds of each outcome should be very visibly displayed in the gui. For partially unknown outcomes (e.g., the result depends on what an enemy has left in reserve), odds are shown for a small range of possibilities, with illustrative pictures showing what each percentage represents.

*) units that cannot be chosen to be engaged (like reserve troops that did not fire on the last round) can still be engaged if they are selected by the engagee. This will likely only happen if they are the only troops left in battle, or if the engagee did not want to reveal them in a potential failed interception maneuver.

*) Each battle has a maximum number of units that can be deployed at the start and on each non-starying round. This does not include intercepting or bombarding units, or those which won their last melee round and are chosing new targets. There is also a maximum number of units that can be deployed at once, and a maximum number that can bombard at once. The latter number is effected by unit range. Any of these maximums may be exceeded, with the chances of doing so modified by tactics values and the amount the maximum is being exceeded by.

1) 1st round of battle
	-Each army chooses up to x units to deploy, where x is determined by the terrain, possibly technology, possibly unit type (e.g. fewer cavalry in forests
	-take turns choosing units to assign. Each unit is assigned by a player chosen pseudo-randomly, weighted by generalship quality and unit abilities.
		-in first round, all units sent forward by one side must be assigned before any "doubling up" can occur. Tripling up happens only after all units on one side are doubled, etc.
		-there is no flanking bonus in the first round
	-once all engaged units are assigned, ranged units in reserve may choose targets. Again, for each ranged unit which fires, a random choice is made about which player assigns the target (longer ranged units are more likely to be able to choose their targets, among other effects). Targets in the first round may only be units committed to the battle, and ranged attacks are resolved before melee combat. 
		-some ranged units may have multiple attacks. These are treated separately for the purpose of choosing targets, so an archer with two attacks may have one target selected by his player and the other selected by his enemy.

2) Subsequent rounds

	-Any committed unit can attempt to disengage, returning it to the reserve (it may immediately re-engage). The result of such an attempt can be A) successful disengagement, B) failed disengagement with no penalty, C) failed disengagement with a penalty in the next round. Results are determined by tactics ratings and attributes of the unit and those it is currently engaged with.
	
	-Units in reserve (including those that just disengaged) and units that destroyed their enemies on their last turn may choose new targets, applying the same process as in the first round, with several differences:
		-As before, all units that will be engaging must be selected at the start of this segment of the round (after disengagements are resolved)
		-Units that won their battles have a tactics advantage over units in reserve. They may also choose to return to the reserve with no roll necessary.
		-Units may attempt to engage troops in reserve that are revealed but not engaged (i.e. those that fired or attempted an intercept on the last round). They do so at a tactics disadvantage that corresponds to the maximum firing range and speed of their victims, among other usual factors. Hiding ability would also be relevant here.
		-Units may attempt to engage enemies that are already engaged. However, their likelihood of succeeding is reduced for each unit the target is already engaged with. If they do succeed in engaging, they also have a chance (as always, modified by tactics ratings and unit type) of gaining a flanking bonus on the next round.
		-When a unit attempts to engage, the enemy may choose a reserve unit to attempt an interception. Intercepting units gain a tactics advantage which is related to their speed/hiding ability (the hiding effect is reduced if they are revealed). If it wins the tactics roll, the intercepting unit must be chosen as the engagee of the initial engager. It has a chance (smaller than for a double-teaming unit) of gaining a flanking bonus.
	
	-Only once all committed units are assigned do ranged units choose to fire and select targets. Units that are engaged cannot bombard, though they may be entitled to first strike attacks.
	
3) Morale - None for now.

4) Pursuit - None; dead units stay dead.
	

'''

from units import *



Class

