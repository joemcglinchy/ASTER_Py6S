import os, sys
import subprocess
import multiprocessing

   
# define a function for mapping across the cmd list    
def scall(c):
    
    return subprocess.call(c, shell=False)
    
    



if __name__ == '__main__':

    ## specify some ASTER band names
    # ASTER_B1 = (-128, 0.485, 0.6425)
    # ASTER_B2 = (-129, 0.590, 0.730)
    # ASTER_B3N = (-130, 0.720, 0.9075)
    # ASTER_B3B = (-131, 0.720, 0.9225)
    # ASTER_B4 = (-132, 1.57, 1.7675)
    # ASTER_B5 = (-133, 2.120, 2.2825)
    # ASTER_B6 = (-134, 2.150, 2.295)
    # ASTER_B7 = (-135, 2.210, 2.39)
    # ASTER_B8 = (-136, 2.250, 2.244)
    # ASTER_B9 = (-137, 2.2975, 2.4875)

    aster_bands = ['ASTER_B1',
                    'ASTER_B2',
                    'ASTER_B3N',
                    'ASTER_B3B',
                    'ASTER_B4',
                    'ASTER_B5',
                    'ASTER_B6',
                    'ASTER_B7',
                    'ASTER_B8',
                    'ASTER_B9']
                    
    ## specify the build type
    #btype = 'test'
    btype = 'full' # required for actual processing, but make sure the syntax is right first with 'test'

    ## specify an aerosol profile
    # NoAerosols = 0
    # Continental = 1
    # Maritime = 2
    # Urban = 3
    # Desert = 5
    # BiomassBurning = 6
    # Stratospheric = 7

    aero = 'Continental'


    # structure the command lists for each aster band
    cmd_list = []
    py = r"C:\anaconda3\envs\arcsienv\python.exe"
    pyfile = r"C:\tools\py6s_emulator\6S_emulator\LUT_build.py"
    for ab in aster_bands:
        # this_cmd = ['python', 'LUT_build.py', '--channel', ab, '--aerosol', aero, '--build_type', btype]
        this_cmd = [py, pyfile, '--channel', ab, '--aerosol', aero, '--build_type', btype]
        cmd_list.append(this_cmd)
        print(this_cmd)
        
    # print('mapping')
    # map(scall, cmd_list)
    # a = list(map(sq, [1,2,3,4,5]))
    # print(a)
    
    count = multiprocessing.cpu_count() - 2
    pool = multiprocessing.Pool(processes=count)
    print (pool.map(scall, cmd_list))
    
    # for cmd in cmd_list:
        # subprocess.call(cmd)