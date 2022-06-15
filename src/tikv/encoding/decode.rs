use std::convert::TryInto;

use super::DataType;
use tikv_client::{Key, Value};

pub struct KeyDecoder {}

impl KeyDecoder {
    #[allow(dead_code)]
    pub fn decode_string(key: Key) -> Vec<u8> {
        let mut bytes: Vec<u8> = key.into();
        bytes.drain(15..).collect()
    }

    pub fn decode_key_type(value: &[u8]) -> DataType {
        match value[0] {
            0 => DataType::String,
            1 => DataType::Hash,
            2 => DataType::List,
            3 => DataType::Set,
            4 => DataType::Zset,
            _ => panic!("no support data type"),
        }
    }

    pub fn decode_key_ttl(value: &[u8]) -> u64 {
        u64::from_be_bytes(value[1..9].try_into().unwrap())
    }

    pub fn decode_topo_key_addr(value: &[u8]) -> &[u8] {
        &value[4..]
    }

    pub fn decode_topo_value(value: &[u8]) -> u64 {
        u64::from_be_bytes(value.try_into().unwrap())
    }

    pub fn decode_key_string_value(value: &[u8]) -> Value {
        value[9..].to_vec()
    }

    pub fn decode_key_string_slice(value: &[u8]) -> &[u8] {
        &value[9..]
    }

    pub fn decode_key_version(value: &[u8]) -> u16 {
        u16::from_be_bytes(value[9..11].try_into().unwrap())
    }

    pub fn decode_key_index_size(value: &[u8]) -> u16 {
        u16::from_be_bytes(value[11..].try_into().unwrap())
    }

    pub fn decode_key_meta(value: &[u8]) -> (u64, u16, u16) {
        (
            Self::decode_key_ttl(value),
            Self::decode_key_version(value),
            Self::decode_key_index_size(value),
        )
    }

    pub fn decode_key_hash_userkey_from_datakey(rkey: &str, key: Key) -> Vec<u8> {
        let key: Vec<u8> = key.into();
        let idx = 10 + rkey.len();
        key[idx..].to_vec()
    }

    /// return (ttl, version, left, right)
    pub fn decode_key_list_meta(value: &[u8]) -> (u64, u16, u64, u64) {
        (
            u64::from_be_bytes(value[1..9].try_into().unwrap()),
            u16::from_be_bytes(value[9..11].try_into().unwrap()),
            u64::from_be_bytes(value[11..19].try_into().unwrap()),
            u64::from_be_bytes(value[19..].try_into().unwrap()),
        )
    }

    pub fn decode_key_set_member_from_datakey(rkey: &str, key: Key) -> Vec<u8> {
        let key: Vec<u8> = key.into();
        let idx = 10 + rkey.len();
        key[idx..].to_vec()
    }

    #[allow(dead_code)]
    pub fn decode_key_zset_member_from_scorekey(rkey: &str, key: Key) -> Vec<u8> {
        let key: Vec<u8> = key.into();
        let idx = 19 + rkey.len();
        key[idx..].to_vec()
    }

    pub fn decode_key_zset_score_from_scorekey(rkey: &str, key: Key) -> i64 {
        let key: Vec<u8> = key.into();
        let idx = 10 + rkey.len();
        i64::from_be_bytes(key[idx..idx + 8].try_into().unwrap())
    }

    pub fn decode_key_zset_member_from_datakey(rkey: &str, key: Key) -> Vec<u8> {
        let key: Vec<u8> = key.into();
        let idx = 10 + rkey.len();
        key[idx..].to_vec()
    }

    pub fn decode_key_zset_data_value(value: &[u8]) -> i64 {
        i64::from_be_bytes(value[..].try_into().unwrap())
    }
}
