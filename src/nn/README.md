## Notes on a machine learning approach to strategy.

Ideas:

 * Onehot on the tile values.  ~256 boolean inputs.
 * Exponentials are a pain.  Don't estimate score, estimate turns of play
   remaining as a proxy for eventual score.
 * We don't need to build a strategy NN on a Q function because there are
   only four moves.  We can run max(Q) directly.
 * There are symmetries but they don't look convolutional.  Probably not a
   convnet.
 * Network will need to understand patterns of lines related to patterns
   of crossing lines.  This means at least two hidden layers.
   * Minimum complexity features are "this line will produce tile K at
     position P" -> 1024 features in the first hidden layer?
   * 256 inputs -> 1024 hidden -> 256 hidden -> 16 hidden -> 1 output?
 * Q-only approach:
   * Train network N1 predicting length of random play.
   * Transfer learn to N2 predicting length of max(N1) play.
   * Iterate.
   * Explore/exploit tradeoff in this approach?  Consider injecting
     random moves per reinforcement learning.
 * Dropout training?  Is there overfitting risk?
   * Each network will need ~10M moves to train on.  How slow is this to
     generate?

