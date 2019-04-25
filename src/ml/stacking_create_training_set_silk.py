import optparse
from collections import defaultdict
import numpy as np

#we need to parse the ensemble duke output raw file, which contains the outputs of N different configurations of duke
#in the file, the output of each configuration is separated by "End of run"
#we need to create a Nx20 matrix, in which the rows are the id1,id2 pairs and the columns are the different N configuration
#The element is 1 if the N-th configuration finds the (id1,id2) and 0 otherwise

def stacking_create_training_set_silk(input_file_name,output_file_name,gold_standard_name,N):

      input_read = open(input_file_name,'rU') #read input file
      train = open(output_file_name,'w') #write on output file
      gold_standard_read = open(gold_standard_name,'rU')

      training_dict = defaultdict(list) #for each pair id1,id2 the list of configuration where it is found as integer k
      gold_standard = {}

      #here we build a dictionary containing the gold_standard, (id1,id1) : 1 or 0

      for i in gold_standard_read.readlines():
        i = i.split(',') #split at commas
        if i[0] == '+': #TP
           gold_standard[(i[1],i[2])] = 1
        elif i[0] == '-': #FP
           gold_standard[(i[1],i[2])] = 0

      ##dictionary: {(id1,id2) : [list_of_configuration_where_the_match_is_found]}

      k = 0 #counter

      #file to parse
      #<http://dbpedia.org/resource/Where_Are_My_Children%3F>  <http://www.w3.org/2002/07/owl#sameAs>  <http://data.linkedmdb.org/resource/film/236>

      for line in input_read.readlines(): #iterate through the lines of the file

          line = line.split(' ') #split when there's a space

          if line[0] == 'End': #we need to pass to the next configuration
              k += 1
              continue

          ID1_whole = line[0] #<http://dbpedia.org/resource/Where_Are_My_Children%3F>, first element of the list
          ID2_whole = line[-2] #<http://data.linkedmdb.org/resource/film/236> , second last element of the list

          #ID1_whole = ID1_whole.split('/')
          #ID2_whole = ID2_whole.split('/')

          #ID1 = ID1_whole[-1].strip('>') #select only the last part, Where_Are_My_Children%3F
          #ID2 = ID2_whole[-1].strip('>') #select only the last part, 236

          ID1 = ID1_whole.strip('<').strip('>')
          ID2 = ID2_whole.strip('<').strip('>')

          training_dict[(ID1,ID2)].append(k)

      #write the header

      train.write('ID1,')
      train.write('ID2,')

      for i in range(N):
        conf = 'C%d' %i
        train.write(conf)
        train.write(',')

      train.write('y') #true class
      train.write('\n')

      #now we create the training set, which contains all the matches that are found positive and that are annotated in the GS

      n = 0

      training_array = np.zeros((len(training_dict), N+1), dtype = int) #number of distinct pairs as number of rows, n_of of config + 1 columns

      for i,j in training_dict.keys():

        try:
          training_array[n,N] = gold_standard[(i,j)] #assign the class label

          positive_values = training_dict[(i,j)] #this is the list of the elements that need to be =1, e.g. [2,10,11,13,14]

          for l in positive_values:
            training_array[n,l] = 1

          train.write(i) #write ID1
          train.write(',')
          train.write(j) #write ID2

          for number in training_array[n]: #now we write the actual values
            train.write(',')
            train.write(str(number))

          train.write('\n')
          n += 1

        except KeyError: #if a match is not annotated in the gs, then it is removed from the training set because we don't know the class label
          continue

      #add to the bottom the lists of matches that are annotated as '+' in the GS and that no configuration is finding

      for i,j in gold_standard.keys():

        if gold_standard[(i,j)] == 1: #real match

            if len(training_dict[(i,j)]) == 0: #it means that no configuration has found it and we add a list of zeros to the training [0,0,0...0]

              zero_array = np.append(np.zeros(N,dtype = int),1)

              train.write(i)
              train.write(',')
              train.write(j)

              for number in zero_array:

                train.write(',')
                train.write(str(number))

              train.write('\n')

      input_read.close()
      gold_standard_read.close()
      train.close()

if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('-i','--input', dest = 'input_file_name', help = 'input_file_name')
    parser.add_option('-g','--gold', dest = 'gold_standard_name', help = 'gold_standard_name')
    parser.add_option('-o','--output', dest = 'output_file_name', help = 'output_file_name')
    parser.add_option('-N','--number', dest = 'number_of_configurations', help = 'number_of_configurations', type = int)

    (options, args) = parser.parse_args()

    if options.input_file_name is None:
       options.input_file_name = raw_input('Enter input file name:')

    if options.output_file_name is None:
        options.output_file_name = raw_input('Enter output file name:')

    if options.gold_standard_name is None:
        options.gold_standard_name = raw_input('Enter gold standard file name:')

    if options.number_of_configurations is None:
        options.number_of_configurations = raw_input('Enter number of configurations:')

    input_file_name = options.input_file_name
    output_file_name = options.output_file_name
    gold_standard_name = options.gold_standard_name
    N = options.number_of_configurations

    stacking_create_training_set_silk(input_file_name,output_file_name,gold_standard_name,N)
