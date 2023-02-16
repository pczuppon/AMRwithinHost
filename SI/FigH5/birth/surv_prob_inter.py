import numpy as np
import matplotlib.pyplot as plt
import os
from numpy import genfromtxt
from scipy.special import hyp2f1
from scipy.special import expi

################################
################################ data
################################

os.chdir(os.path.realpath(''))

################################
################################ Parameter definitions
################################

################################ Logistic growth dynamics
bS = 2.5
bR = 2.225
dS = 0.5
dR = 0.5

gamma = 1.

K = 1000

N0 = (bS-dS)*K/gamma

################################ Antimicrobial response / Pharmacodynamics
c = np.arange(0,2000,0.1)

def a(c,X):
    if (X==0):
        psimax = bS-dS
        mic = 20
    if (X==1):
        psimax = bR-dR
        mic = 20*10
    psimin = np.log(10)*(-3)*24
    kappa = .25
    
    return((psimax-psimin)*(c/mic)**kappa / ((c/mic)**kappa -psimin/psimax))

################################ Finding the time where birth rate becomes positive
def time(a_S,a_R):
    t = 0
    dt = 0.001
    n = N0
    while(bR-a_R-gamma*(n+1)/K <= 0):
        rhoS = max(0,bS-gamma*n/K-a_S) - dS
        n = n + dt*n*rhoS
        t += dt
        if (t>TT):
            break
    
    return(t)



################################
################################ Surv prob at time t - bacteriostatic
################################
surv_bs = []
survinf_bs = []
TT = 7
TTinf = 100
N0 = (bS-dS)*K/gamma
for i in range(len(c)):
    rhoS = max(bS-a(c[i],0),0)-dS   # < 0 ab i = 171
    rhoR = max(bR-a(c[i],1),0)-dR   # < 0 ab i = 1170
    
    s = rhoR-rhoS
    
    print(i)
    
    dt = 0.01
    ############## sensitive strain exponentially declining for all t
    if (bS < a(c[i],0)):
        # time until growth rate of the resistant type becomes positive
        if (bR-a(c[i],1) > 0):
            TT1 = min(TT,max(0,-np.log(((bR-a(c[i],1))*K/(gamma))/N0)/dS))
            TT1inf = max(0,-np.log(((bR-a(c[i],1))*K/(gamma))/N0)/dS)
            # sensitive abundance at TT1
            N0alt = max(0,N0*np.exp(-dS*TT1))
            N0altinf = max(0,N0*np.exp(-dS*TT1inf))
            # compute integral of survival probability numerically
            integral_time = np.arange(TT1,TT,dt)
            integral = 0
            for j in range(len(integral_time)):
                integral += dt*np.exp((integral_time[j]-TT1)*(a(c[i],1)-bR+dR) + gamma*(1-np.exp(-(integral_time[j]-TT1)*dS))*N0alt/(K*dS))*dR
            
            # multiply this survival probability with probability of no death until TT1
            surv_bs.append( np.exp(-dR*TT1)/(1+integral)) 
            
            # compute integral of survival probability numerically
            integral_time = np.arange(TT1inf,TTinf,dt)
            integral = 0
            for j in range(len(integral_time)):
                integral += dt*np.exp((integral_time[j]-TT1inf)*(a(c[i],1)-bR+dR) + gamma*(1-np.exp(-(integral_time[j]-TT1inf)*dS))*N0altinf/(K*dS))*dR
            survinf_bs.append( max(np.exp(-dR*TT1inf)/(1+integral),0))
        
        else:
            surv_bs.append(np.exp(-dR*TT))
            survinf_bs.append(0)
    
    else:
        TTS = min(TT,max(0,-np.log(((bS-a(c[i],0))*K/(gamma))/N0)/dS))          ## time until sensitive strain is exponentially declining
        TTR = min(TT,max(0,-np.log(((bR-a(c[i],1))*K/(gamma))/N0)/dS))          ## time until resistant strain is not reproducing (always smaller than TTS!)
        # sensitive abundance at TTR
        N0atR = max(0,N0*np.exp(-dS*TTR))
        # sensitive abundance at TTS
        N0atS = max(0,N0*np.exp(-dS*TTS))
        
        # infinite treatment scenario:
        TTSinf = max(0,-np.log(((bS-a(c[i],0))*K/(gamma))/N0)/dS)
        TTRinf = max(0,-np.log(((bR-a(c[i],1))*K/(gamma))/N0)/dS)
        N0atRinf = max(0,N0*np.exp(-dS*TTRinf))
        N0atSinf = max(0,N0*np.exp(-dS*TTSinf))
        
        ### if sensitive strain initially declines exponentially!
        if (TTS > 0):
            
            # compute integral of survival probability numerically between TTR and TTS
            integral_time = np.arange(TTR,TTS,dt)
            integral = 0
            for j in range(len(integral_time)):
                integral += dt*np.exp((integral_time[j]-TTR)*(a(c[i],1)-bR+dR) + gamma*(1-np.exp(-(integral_time[j]-TTR)*dS))*N0atRinf/(K*dS))
                   
            denom = (1+integral*dR)
            A = np.exp( gamma*(1-np.exp(-dS*(TTS-TTR)))*N0atRinf / (dS*K) + (TTS-TTR)*(dR+a(c[i],1)-bR)) 
            B = 1 - A + integral*dR
            
            
            offspring = 10
            j=1
            survival = 0
            countprob = 0
            while (j<offspring):
                F = F = (dR*(rhoR*gamma*N0atSinf*(1-np.exp(-s*(TTinf-TTS))) - s*(gamma*N0atSinf - K*rhoS) * (1-np.exp(-rhoR*(TTinf-TTS)))) / (K*rhoR*rhoS*s + dR*(rhoR*gamma*N0atSinf*(1-np.exp(-s*(TTinf-TTS))) - s*(gamma*N0atSinf - K*rhoS) * (1-np.exp(-rhoR*(TTinf-TTS))))))**j
                prob = A * B**(j-1) / (denom**(j+1))
                countprob += prob
                survival += (1-F)*prob
                j += 1
            
            survinf_bs.append(max(0,min(1,np.exp(-dR*TTR)* (survival+1-countprob-1-1/(-A-B)))))
            
            
            if (TTS < TT):
                # compute integral of survival probability numerically between TTR and TTS
                integral_time = np.arange(TTR,TTS,dt)
                integral = 0
                for j in range(len(integral_time)):
                    integral += dt*np.exp((integral_time[j]-TTR)*(a(c[i],1)-bR+dR) + gamma*(1-np.exp(-(integral_time[j]-TTR)*dS))*N0atR/(K*dS))
                       
                denom = (1+integral*dR)
                A = np.exp( gamma*(1-np.exp(-dS*(TTS-TTR)))*N0atR / (dS*K) + (TTS-TTR)*(dR+a(c[i],1)-bR)) 
                B = 1 - A + integral*dR
                
                offspring = 10
                j=1
                survival = 0
                countprob = 0
                while (j<offspring):
                    F = (dR*(rhoR*gamma*N0atS*(1-np.exp(-s*(TT-TTS))) - s*(gamma*N0atS - K*rhoS) * (1-np.exp(-rhoR*(TT-TTS)))) / (K*rhoR*rhoS*s + dR*(rhoR*gamma*N0atS*(1-np.exp(-s*(TT-TTS))) - s*(gamma*N0atS - K*rhoS) * (1-np.exp(-rhoR*(TT-TTS))))))**j
                    prob = A * B**(j-1) / (denom**(j+1))
                    countprob += prob
                    survival += (1-F)*prob
                    j += 1
                
                surv_bs.append(np.exp(-dR*TTR)* (survival+1-countprob-1-1/(-A-B))) 
                
            else:
                integral_time = np.arange(TTR,TT,dt)
                integral = 0
                for j in range(len(integral_time)):
                    integral += dt*np.exp((integral_time[j]-TTR)*(a(c[i],1)-bR+dR) + gamma*(1-np.exp(-(integral_time[j]-TTR)*dS))*N0atR/(K*dS))
                
                surv_bs.append(np.exp(-dR*TTR)/(1+integral*dR))
        
        ##### if sensititve strain does not decline exponentially
        else:
            F = K*rhoR*rhoS*s / (K*rhoR*rhoS*s + dR*(rhoR*gamma*N0atS*(1-np.exp(-s*(TT))) - s*(gamma*N0atS - K*rhoS) * (1-np.exp(-rhoR*(TT)))))
            F2 = K*rhoR*rhoS*s / (K*rhoR*rhoS*s + dR*(rhoR*gamma*N0atS*(1-np.exp(-s*(TTinf))) - s*(gamma*N0atS - K*rhoS) * (1-np.exp(-rhoR*(TTinf)))))
            surv_bs.append(F)
            survinf_bs.append(max(0,F2))

i = 200
surv_bs[i] = (surv_bs[i-1] + surv_bs[i+1])/2
survinf_bs[i] = (survinf_bs[i-1]+survinf_bs[i+1])/2

i = 2000
surv_bs[i] = (surv_bs[i-1] + surv_bs[i+1])/2
survinf_bs[i] = (survinf_bs[i-1]+survinf_bs[i+1])/2


############# bacteriocidic
surv_bc = []
survinf_bc = []
N0 = (bS-dS)*K/gamma
for i in range(len(c)):
    rhoS = bS-a(c[i],0)-dS
    rhoR = bR-a(c[i],1)-dR
    s = rhoR-rhoS
    
    F = K*s*rhoS*rhoR / (K*s*rhoS*rhoR + (dR + a(c[i],1)) * (N0 * gamma * rhoR * (1-np.exp(-s*TT)) + s * (rhoS*K - N0*gamma)*(1-np.exp(-rhoR*TT))))
    F2 = K*s*rhoS*rhoR / (K*s*rhoS*rhoR + (dR + a(c[i],1)) * (N0 * gamma * rhoR * (1-np.exp(-s*TTinf)) + s * (rhoS*K - N0*gamma)*(1-np.exp(-rhoR*TTinf))))
    surv_bc.append(max(0,F))
    survinf_bc.append(max(0,F2))

i = 200
surv_bc[i] = (surv_bc[i-1] + surv_bc[i+1])/2
survinf_bc[i] = (survinf_bc[i-1]+survinf_bc[i+1])/2

i = 2000
surv_bc[i] = (surv_bc[i-1] + surv_bc[i+1])/2
survinf_bc[i] = (survinf_bc[i-1]+survinf_bc[i+1])/2



################################
################################ Plot surv prob
################################
plt.semilogx(c,surv_bs,linewidth=2)
plt.semilogx(c,surv_bc,linewidth=2)
plt.vlines(c[200],0,.75,linestyle='dashed',lw=2,color='black')
plt.plot(c,survinf_bs,color='C0',linewidth=2,linestyle='dashed')
plt.plot(c,survinf_bc,color='C1',linewidth=2,linestyle='dashed')
plt.tick_params(axis='both', which='major', labelsize=15, width=1, length=10)
plt.tick_params(axis='both', which='minor', labelsize=10, width=1, length=5)
plt.ylim((-0.025,0.8))
plt.show()




