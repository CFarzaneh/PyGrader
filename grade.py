import os
import tarfile
from shutil import copyfile
from subprocess import Popen,PIPE,STDOUT
import glob
import shutil
from time import sleep
import sys

path = '/home/grads/farzaneh/grading/'
untarsubmissions = 'untarsubmissions'

errorFile = open('err.txt','w+')

numCompilerErrors = 0
headersNotFound = 0
noHeaders = []

for file in sorted(os.listdir('submissions')):
	if file.endswith('.tar.gz'):
		name = file.split('_')[0]
		
		if name == 'grantgesabigail' or name == 'pregasenmelissa' or name == 'aguilaalexis' or name == 'caldwellwalter':
			continue

		print('\nStudent',name)
		os.chdir(path)

		tar = tarfile.open(path + 'submissions/'+file)
		tar.extractall(path=untarsubmissions)
		tar.close()

		os.system('find . -name \'.*\' -exec rm -rv {} +')

		folder = os.listdir(untarsubmissions)
		if 'date.h' in folder or 'Date.h' in folder:
			os.chdir(path+'untarsubmissions/')
			filesThatNeedMoving = glob.glob('*')
			os.mkdir(path+untarsubmissions+'/'+name)
			for fileMoving in filesThatNeedMoving:
				os.rename(path+untarsubmissions+'/'+fileMoving, path+untarsubmissions+'/'+name+'/'+fileMoving)
			os.chdir('..')

		folder = os.listdir(untarsubmissions)[0]
		os.chdir(path+'untarsubmissions/'+folder)

		if 'date.h' not in os.listdir() and 'Date.h' not in os.listdir():
			here = glob.glob('**/*.h', recursive=True)[0]
			os.chdir('..')
			if 'date.h' in here or 'Date.h' in here:
				here = glob.glob('**/*.h', recursive=True)[0]
				dirs = here.split('/')
				os.makedirs(dirs[-2])
				for fileThatNeedMoving in os.listdir('/'.join(dirs[:-1])):
					os.rename('/'.join(dirs[:-1])+'/'+fileThatNeedMoving,dirs[-2]+'/'+fileThatNeedMoving)
				shutil.rmtree(path+untarsubmissions+'/'+dirs[0])
				folder = os.listdir()[0]
				os.chdir(folder)
			else:
				print('Skipping',name,'because header not found')
				headersNotFound+=1
				noHeaders.append(name)
				os.chdir('..')
				shutil.rmtree(folder)
				os.chdir('..')
				continue

		for files in os.listdir():
			if files != 'date.cpp' and files != 'date.h' and files != 'Date.cpp' and files != 'Date.h':
				os.remove(files)

		copyfile(path+'codeDestroyer.cpp','codeDestroyer.cpp')
		copyfile(path+'run.txt','run.txt')

		cppFiles = glob.glob('*.cpp')
		cppFiles.insert(0,'-std=c++11')
		cppFiles.insert(0,'g++')

		print('Compiling the code')
		gccCompile = Popen(cppFiles,stderr=STDOUT,stdout=sys.stdout)
		gccOutput, gccStatusCode = gccCompile.communicate()[0],gccCompile.returncode
		if gccStatusCode != 0:
			#print(gccOutput)
			print('An error occured during compiling the code!')
			os.chdir('..')
			shutil.rmtree(folder)
			os.chdir('..')
			numCompilerErrors+=1
			continue
		else:
			print('Compile successful')

		if os.path.isfile(path+'submission_outputs/'+name+'_output.txt'):
			print('Skipping execution for',name)
			os.chdir('..')
			shutil.rmtree(folder)
			os.chdir('..')
			continue

		outputFile = open(name+'_output.txt','w+')
		inputFile = open('run.txt','r')
		print('Running codeDestroyer!')
		execPath = path+untarsubmissions+'/'+folder+'/a.out'
		executeTest = Popen(execPath,stderr=errorFile,stdout=outputFile,stdin=inputFile)
		cont = False
		for i in range(3):
			if executeTest.poll() is not None:
				break
			if i == 2:
				executeTest.kill()
				outputFile.close()
				inputFile.close()
				os.chdir('..')
				shutil.rmtree(folder)
				os.chdir('..')
				cont = True
				print('Timeout!')
				break
			sleep(1)

		if cont == True:
			continue

		executeStatusCode = executeTest.returncode

		if executeStatusCode != 0:
			if executeStatusCode == -11:
				print('Segfault!',executeStatusCode)
				outputFile.write('Segfault\n')
			else:
				print('Error has occured',executeStatusCode)
				outputFile.write('Error '+str(executeStatusCode)+'\n')
		else:
			print('Survived codeDestroyer')


		copyfile(name+'_output.txt',path+'submission_outputs/'+name+'_output.txt')

		outputFile.close()
		inputFile.close()
		os.chdir('..')
		shutil.rmtree(folder)
		os.chdir('..')

errorFile.close()
os.system('rm err.txt')
print('Number of compiler errors:',numCompilerErrors)
print('Number of projects with headers not found:',headersNotFound)
print(noHeaders)
print('\nDone!')