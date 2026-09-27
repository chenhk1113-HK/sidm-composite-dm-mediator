#!/usr/bin/env julia
# T215l — Verify Random.seed!(42) actually seeds the task-local RNG
# used by KiSS-SIDM. Print state before and after a few rand calls.

using DSMC
using Random
using StaticArrays
using Unitful
using UnitfulAstro
using HDF5
using JLD2

println("Test 1: Default RNG state")
Random.seed!(42)
println("First rand after seed: ", rand())

Random.seed!(42)
println("First rand after re-seed: ", rand())
println("(should be the same as above)")

println()
println("Test 2: Task-local RNG state via copy_rng")
rng = Random.default_rng()
Random.seed!(rng, 42)
println("rng_first: ", rand(rng))
Random.seed!(rng, 42)
println("rng_first re-seeded: ", rand(rng))

println()
println("Test 3: thread-local RNG (none in single-thread mode)")
println("Threads.nthreads() = ", Threads.nthreads())

println()
println("Test 4: Check if StatsBase.sample uses main task RNG")
using StatsBase
Random.seed!(42)
s1 = sample(1:100, 5; replace=false)
Random.seed!(42)
s2 = sample(1:100, 5; replace=false)
println("sample reproducibility: s1 == s2 = ", s1 == s2)

println()
println("Test 5: Full chain — Random.seed!(42) → first KiSS-SIDM rand")
Random.seed!(42)
# What KiSS-SIDM sees as the first rand() call
x1 = rand()
Random.seed!(42)
x2 = rand()
println("Direct rand() reproducibility: ", x1 == x2)

println()
println("END OF TEST")