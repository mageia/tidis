pub mod decode;
pub mod encode;

pub const EMPTY_VALUE: Vec<u8> = vec![];

pub enum DataType {
    String,
    Hash,
    List,
    Set,
    Zset,
}

pub use {
    encode::KeyEncoder,
    decode::KeyDecoder,
};