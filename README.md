# Topic-Sensitive Auto Complete
This is a module that updates the [Peter Norvig spell-checker](http://norvig.com/spell-correct.html) by changing the language model priors to match the distribution of a predicted sentence- or document-topic.  I have no idea if this will prove to be a useful endeavour.  My goal is to tune the pipeline to the point where I can achieve similar accuracy to Norvig and then analyze the set of words where my autocompletion out-performed his.  If there are interesting patterns suggesting improved end-user experience, then this will be a success.

## Current Methodology
1. Build topic model on training corpus using Latent Dirichlet Allocation
  * Stop Words ('in', 'the', 'if', etc...) were not removed as they improve accuracy in the current setup
2. Dump word distributions for each topic into a MongoDB database
  * Current version uses the distributional densities of each word in the topic, but future versions will play with the ordering to improve accuracy, as the order is entirely what determines the recommendation
3. Predict topic of current sentence
  * Future versions may predict topic of last n sentences depending on accuracy in testing
4. Use predicted topic to query MongoDB for suggested correction of target word
  * obviously this will need to be sped up if this methodology proves to be useful
5. Test accuracy on a testing corpus of randomly selected documents that were withheld from the training set

## Current Performance Benchmarks
* Test Hit Rate (my module):  
  * 0.65
* Control Hit Rate (Norvig's module):  
  * 0.732