# To avoid repeating expensive data generation and network training steps,
# we use a Makefile to manage the pipeline.


PY=pipenv run python3 -m
all: test generation_3.hdf5
$PHONY: all


# TODO(ggould) add a rule to ensure that we have a good pipenv, or at least
# that we get a readable error if we don't.


# Run unit tests via `make test`.
test:
	$(PY) unittest discover .

$PHONY: test


# Train our first generation model.  It doesn't need much data because
# it is basically very, very stupid (and its input data is nearly random).
#
# Since all our data is generated, the only reason to use more than one
# epoch is that training is faster than generation.  But don't use very
# many epochs:  Training reaches a plateau very quickly, and I have taken
# no measures to avoid overfitting (because data is so cheap).
#
# Expect training to take about five minutes and end up with a mean error
# around 23.  The random strategy on a fairly random game makes it hard to
# predict outcomes with any certainty.
generation_0.npz:
	$(PY) strategy.nn.data --num_examples 500000 --output_file $@

generation_1.hdf5: generation_0.npz
	$(PY) strategy.nn.model --training_data $^ --epochs 4 --model_file $@
	# Evaluate on a new test set.
	$(PY) demo  --strategy $@ --number_of_games 1000 --summary

# This first generation controller is amazingly good, outperforming random by
# a factor of 2-3x.
#
# Intuitively we should be able to generate future generations of controller
# in the same way.  In practice if we do this performance drops back to
# random.  What?  Overfitting -- the training data will never explore any
# non-optimal paths, and so the strategy won't know that they are bad.
#
# TODO(ggould) There are two obvious approaches to avoid this:
#  * Transfer learning.  Gen-1 knew bad from good; learn from it.
#  * Start training data generation from positions from the random set.
