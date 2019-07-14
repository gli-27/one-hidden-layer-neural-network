Backpropagation
---------------- 
Guo Li 
Jan 23 2019 
----------------


Briefly Description
-------------------
This programming assignment is to implement the simple neural network with back propagation update the weights of layers in the network. For this assignment, we will use the same data set as the former one, the adult data set, to build a two-classes model to classify the data set. The main idea of this model is to use neurons to analyze features of the data points and use some weights and activation function to build a nonlinear model to classify. As what the requirement asks we do, we only need to build one hidden layer and an output layer for this assignment. 
The model basically can be divided into two part, forward and backward. For the forward part, we just need to use weights multiply the feature points to get the results and use activation function to turn the results into nonlinear. And here is the formula for this (noticed that we use sigmoid as activation function):

		Zj = sum(Wij*Xi)
		Aj = sigmoid(Zj)

And the backward, aka backpropagation, is an implementation of the chain rule. It starts from the error function we defined (in this assignment, we use the sum of square error function). The main purpose of this step is to modify, to update the weights of each layer to decrease the error function by gradient descend. Note that here we have two set of weights W1 and W2, and their shape will be [FEATURE_NUM, HIDDEN_DIM] and [HIDDEN_DIM+1, 1]. The plus one mean the bias of the hidden layer. We need to update all of them use chain rule.
-------------------


Extra args used in this assignment
----------------------------------
Most args in this assignment are the same with the perceptron assignment and we will not explain them in details here. One thing to noticed that we use the same mode with the usage of dev data, which means you can choose the mode of the usage. And the same as the perceptron, choosing 0 means once the accuracy decrease then we stop, choosing 1 means we will choose the weights unless next 10 iterations' result will not make the accuracy increase. The default value of this mode is 0 and you can implement it as --devmode 0/1. 
Another args we add by ourselves is --plot, whose default value is false, which means simply implement this algorithm will not plot the graphs. Once you provide this argument, this program will run to plot. But noticed that, in this program we chose matplotlib as the plot tool and this is not installed in the server. If you need to plot the pictures, please install the lib in advanced. 
----------------------------------


Performance over hyperparameters (iterations, lr, hidden_dim)
-------------------------------------------------------------
As we stated above, we use sigmoid as the activation function in this assignment. It is a monotonic function and will rapidly converge to 0 or 1 once the independent variable smaller than -5 or greater than 5. The rapidly change interval is between [-5, 5] so that once we derived the derivation of the sigmoid function, we will find that the value of the derivation is relatively large in region [-5, 5] and once the value is out of this region, the gradient will be very small. And for the graph of the sigmoid function and its derivation, please refers to file "sigmoid.png"
This is the basic background to explain the hyperparameters. As what we have already know, the input of the sigmoid function is the multiply of x and weights (for the first hidden layer) and multiply of output and weights (for the output layer). If we use the weights randomly initialized, as we updated them, the result will rapidly become polarization (smaller than -5 or greater than 5). And the result will not change and keep stable as the iteration times goes up. Which will lead the derivation of the error function become very small, which will make the update of the weights become very small either, which will make minor change to the next forward calculation and which will eventually don't make any difference since we use sigmoid activation function and once the result greater than 0.5 we will perceive it's a 1. And this is the reason why the result will converge eventually. 
In practice, the result will converge or not also depend on the learning rate (lr) we choose. Once the lr is relatively large, say equals to 1, the result will not converge. That is because every step we choose to update the weights is too large so that we miss the appropriate value or plateau and pace around it but cannot dive into it. For details, you can refers to "F1.png". You can find the phenomenon in first two plots. But for plots three, you might noticed that it seems like converged in the end in general. This is because the hidden_dim is relatively large and the general result will be stable in general but still fluctuate and have noise. 

To avoid this, we better use a relatively smaller learning rate. Then the next step, we chose lr equals to 0.25 and use this learning rate to calculate the model with hidden_dim equals to 5, 15 and 30. We can noticed that, all of them can converge in a relatively small iteration times. But you can noticed that, for the smaller hidden layer, we need almost 50 iteration times to make it jump into a better result plateau. For more hidden_dim, although we might need relatively more iteration times, we still can dive into the better result plateau relatively quicker. And for the most stable result, we might need more hidden_dim, which is identified with our expectation that if we use more hidden_dim to describe the features, we might get more precisely and stable once we converge. For details, please refer to graph "F2.png"

Furthermore, if we decrease the learning rate again to 0.02. You can find out that, no matter how many we chose as our hidden_dim, the iteration times we need to run to converge become larger obviously. This is because the learning rate is the coefficient of the update formula and once it becomes too small, as a consequence we need more iterations. But once we converge, we might get a relatively more stable result comparing to large learning rate. As for large hidden_dim, we even still cannot perceive any change though 50 iterations. For details, please refer to picture "F3.png"

To choose a relatively good hyperparameters, I personally recommend to chose hidden_dim between 10 to 20, and learning rate between 0.1 to 0.2, iteration more than 10 but less than 30 will give you a relatively good result accuracy. Noticed that, you can chose the learning rate you want but relatively small and hidden_dim you want relatively large but not too large and set the iteration times relatively large. Then choosing the mode like --devmode 1, then we will use dev data set to help you to get the best result and once it's converge, it will stop early.

