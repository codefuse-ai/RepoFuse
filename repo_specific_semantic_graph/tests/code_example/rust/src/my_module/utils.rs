use super::{sub_module::sub_function as sub, bar::*};
use crate::my_other_module::*;

pub fn utility_function() {
    sub();
    bar_function();
    helper::helper_function();
    println!("Hello from utility_function in utils!");
}
