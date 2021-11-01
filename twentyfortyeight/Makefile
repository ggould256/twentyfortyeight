# To avoid repeating expensive data generation and network training steps,
# we use a Makefile to manage the pipeline.


PY=pipenv run python3 -m
all: test random_demo generation_1_demo generation_2_demo
$PHONY: all

clean:
	-rm *.hdf5
	-rm *.npz


# TODO(ggould) add a rule to ensure that we have a good pipenv, or at least
# that we get a readable error if we don't.


# Run unit tests via `make test`.
test:
	$(PY) unittest discover .
$PHONY: test


# Show off how bad things are to start with.
random_demo:
	$(PY) demo --strategy random --number_of_games 1000 --summary
$PHONY: random_demo

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
	$(PY) strategy.nn.model --training_data $< --epochs 4 --model_file $@

generation_1_demo: generation_1.hdf5
	# Evaluate on a new test set.
	$(PY) demo --strategy $< --number_of_games 100 --summary
$PHONY: generation_1_demo

# This first generation controller is amazingly good, outperforming random by
# a factor of 2-3x.
#
# Intuitively we should be able to generate future generations of controller
# in the same way.  In practice if we do this performance drops back to
# random.  What?  Overfitting -- the training data will never explore any
# non-optimal paths, and so the strategy won't know that they are bad.
#
# We use two obvious approaches to avoid this:
#  * Start training data generation from positions from the random set.
#  * Transfer learning.  Gen-1 knew bad from good; learn from it.

# Examples are more expensive to generate, so use fewer examples and more
# training epochs in this generation.
generation_1.npz: generation_1.hdf5 generation_0.npz
	$(PY) strategy.nn.data --strategy $<         \
	                       --num_examples 200000 \
	                       --output_file $@      \
	                       --starting_positions $(word 2,$^) \
	                       --new_start_fraction 0.75

generation_2.hdf5: generation_1.npz generation_1.hdf5
	$(PY) strategy.nn.model --training_data $<   \
	                        --transfer_from $(word 2,$^) \
	                        --epochs 50          \
	                        --model_file $@

generation_2_demo: generation_2.hdf5
	# Evaluate on a new test set.
	$(PY) demo --strategy $< --number_of_games 100 --summary
$PHONY: generation_2_demo
