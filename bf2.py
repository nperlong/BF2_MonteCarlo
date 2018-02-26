#! /usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
import collections

#======================================================

def draw_crate(df,size=1,replace=True):
    refund = 0
    cardArray = np.arange(df.size)+1
    c = np.random.choice(cardArray,size,replace)[0]
    row,col = np.where(cardArray.reshape(df.shape) == c)
    flip = np.random.choice([1,2,3],p=[0.77,0.20,0.03])
    if (df.iloc[row[0]]['Card {}'.format(col[0]+1)] >= flip):
        refund += 300
    
    df.iloc[row[0]]['Card {}'.format(col[0]+1)] = flip
    

    return refund
#=========================================================
def draw_multiple(df,size=2,replace=False):
    refund = 0
    cardArray = np.arange(df.size)+1
    cardlist = np.random.choice(cardArray,size,replace)
    for c in list(cardlist):
        row,col = np.where(cardArray.reshape(df.shape) == c)
        ind = 'Card {}'.format(col[0]+1)
        flip = np.random.choice([1,2,3],p=[0.77,0.20,0.03])
        
        if (df.iloc[row[0]][ind] >= flip):
            refund += 300
            
        df.iloc[row[0]][ind] = flip

    return refund

#=======================================================================
def init_portfolio():
    sTroopers = ['Assault','Heavy','Officer','Specialist']
    sEnforce = ['Enforcer','Aerial']
    sHeros = ['Rey','Kylo','Yoda','Chewie','Han','Vader','Boba','Bossk','Sidious'
              ,'Maul','Luke','Leia','Lando','Iden','Finn','Phasma']
    sShips = ['Fighter','Interceptor','Bomber','HanChew','HanRey','Kylo','Vader',
              'Boba','Yoda','Poe','Luke','Maul','Tallie','Iden']
    
    columns1 = ['Card {}'.format(s+1) for s in range(17)] 
    columns2 = ['Card {}'.format(s+1) for s in range(9)]
    columns3 = ['Card {}'.format(s+1) for s in range(5)]
    
    troopers = pd.DataFrame(0, index=sTroopers,columns=columns1)
    enforcers = pd.DataFrame(0, index=sEnforce,columns=columns3)
    heros = pd.DataFrame(0, index=sHeros,columns=columns2)
    ships = pd.DataFrame(0, index=sShips,columns=columns2)

    return troopers, enforcers, heros, ships

#===========================================================================    
totalCrates = 5000

nTroopers = 4
nEnforce = 2
nHeros = 16
nRegShips = 3
nHeroShips = 11
nShips = nRegShips + nHeroShips

nTrooperCards = nTroopers*17
nEnforceCards = nEnforce*5
nHeroCards = nHeros*9
nShipCards = (nRegShips+nHeroShips)*9
nCards = nTrooperCards + nHeroCards + nShipCards + nEnforceCards

#craftCost = nCards*40

probTroop = nTrooperCards/(nEnforceCards+nTrooperCards)

tcrate = 4400
scrate = 2400
hcrate = 2200
nCrates = np.arange(totalCrates)
nSims = 10

allCards = np.zeros(nSims,dtype=object)
allCost = np.zeros(nSims,dtype=object)
allCredits =np.zeros(nSims,dtype=object)
for sim in range(nSims):
    print (sim)
    troopers, enforcers, heros, ships = init_portfolio()
    totalCards = np.zeros(totalCrates)
    craftCost = np.zeros(totalCrates)
    CreditsSpent = np.zeros(totalCrates)
    craftParts = 0
    Credits  = 0
    for n in nCrates:
        Credits = hcrate

        #determine how many cards you get in this crate
        nsamples= np.random.randint(1,3) 
        #determine which other type of card you get
        crate2 = np.random.randint(0,3)
        #it could be a 3rd card from the same type
        if not crate2:
            nsamples +=1
            
        if nsamples >1:
            Credits -= draw_multiple(heros,size=nsamples)
        else:
            Credits -= draw_crate(heros)

        if crate2 == 1:
            #sample from troopers
            #choose between enforcer cards and regular trooper cards
            flip = np.random.choice([0,1],p=[probTroop,1-probTroop])
            if not flip:
                Credits -= draw_crate(troopers)
            else:
                Credits -= draw_crate(enforcers)
        elif crate2 == 2:
            #sample from ships
            Credits -= draw_crate(ships)


        if nsamples >2:
            craftParts += 35
        else:
            craftParts += 50
            
        CreditsSpent[n] = Credits
        #craftCost[n] = (nCards - totalCards[n])*40 - craftParts
        cardLevels = collections.Counter(troopers.values.flatten()) + \
                     collections.Counter(enforcers.values.flatten()) + \
                     collections.Counter(heros.values.flatten()) + \
                     collections.Counter(ships.values.flatten())

        totalCards[n] = sum(c for c in cardLevels.values()) - cardLevels[0]
        
        #craftCost[n] = (nCards - totalCards[n])*40 - craftParts
        craftCost[n] = cardLevels[0]*(40+80+120) \
                          + cardLevels[1]*(80+120)  + cardLevels[2]*(120) \
                          + cardLevels[3]*(0) -craftParts
    
        if craftCost[n] <= 0:
            allCards[sim] = totalCards[:n+1]
            allCost[sim] = craftCost[:n+1]
            allCredits[sim] =CreditsSpent[:n+1]
            break

f = plt.figure()
ax = plt.subplot(311)
ax2 = plt.subplot(312,sharex=ax)
ax3 = plt.subplot(313,sharex=ax)   
aveCredits = 0
aveCrates = 0
credPerHour = 2500

leastCrates = np.argmin(np.array([np.cumsum(s)[-1] for s in allCredits]))
mostCrates = np.argmax(np.array([np.cumsum(s)[-1] for s in allCredits]))

for sim in range(nSims):
    nCrates = np.arange(len(allCards[sim]))
    cumCredits = np.cumsum(allCredits[sim],dtype=float)
    aveCredits += cumCredits[-1]
    aveCrates += nCrates[-1]
    
    if sim == mostCrates:
        ax.plot(nCrates,allCards[sim],'g-',label='Least Lucky')
        ax2.plot(nCrates,allCost[sim],'g-',label='Least Lucky')
        ax3.plot(nCrates,cumCredits,'g--')
    elif sim ==leastCrates:
        ax.plot(nCrates,allCards[sim],'r-',label='Most Lucky')
        ax2.plot(nCrates,allCost[sim],'r-', label='Most Lucky')
        ax3.plot(nCrates,cumCredits,'r-')
        

print ('Average Credits Spent: {}'.format(aveCredits/nSims + 75000))
print ('Average Crates Opened: {}'.format(aveCrates/nSims))
print('Average Hours to unlock all {}'.format((aveCredits/nSims + 75000)/credPerHour))

axarr = [ax,ax2,ax3]
labels =['Star Cards Acquired','Crafting Parts Needed\n to Purchase Remaining Cards','Credits Spent']
for i,x in enumerate(axarr):
    x.grid()
    x.text(0.5, 0.98, labels[i],fontsize=14.0,fontstyle='oblique',
           horizontalalignment='center',fontweight='bold',
           verticalalignment='top',
           transform=x.transAxes)
    if i == 0:
        x.legend()
    if i==2:
        ax3.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
        ax3.plot(nCrates,nCrates*2200,'k-',label='Theoretical Max (no Refunds)')
        ax3.set_ylim([0,(n+1)*2200])
        ax3.set_xlabel('Crates Opened',fontsize=14.0)
        ax3.legend()



plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
f.subplots_adjust(hspace=0)
f.suptitle('Monte Carlo - Acquire all blue cards and heros',fontsize=16.0)
plt.show()


#=================================================
