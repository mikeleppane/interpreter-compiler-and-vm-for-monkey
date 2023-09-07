use std::time::Instant;

fn fibonacci(n: u32) -> u32 {
    if n == 0 {
        return 0
    }
    if n == 1 {
        return 1
    }
    fibonacci(n - 1) + fibonacci(n - 2)
}

fn main() {
    let start = Instant::now();
    fibonacci(35);
    let duration = start.elapsed();

    println!("Fibonacci(35) in Rust 1.72: execution time in seconds is: {:?}", duration);
}
