use std::sync::Arc;

use bytes::Bytes;
use tikv_client::Transaction;
use tokio::sync::Mutex;

use crate::{utils::resp_err, Frame};

use super::errors::{AsyncResult, REDIS_NOT_SUPPORTED_ERR};

#[derive(Clone)]
pub struct ConfigCommandCtx {
    // txn: Option<Arc<Mutex<Transaction>>>,
}

impl ConfigCommandCtx {
    pub fn new(_txn: Option<Arc<Mutex<Transaction>>>) -> Self {
        ConfigCommandCtx {}
    }

    pub async fn do_async_rawkv_get(&self, key: &str, field: &str) -> AsyncResult<Frame> {
        if let "get" = key.to_lowercase().as_str() {
            match field.to_lowercase().as_str() {
                "save" => Ok(Frame::Array(vec![
                    Frame::Simple("save".into()),
                    Frame::Bulk(Bytes::from("3600 1 300 100 60 10000")),
                ])),
                "appendonly" => Ok(Frame::Array(vec![
                    Frame::Simple("appendonly".into()),
                    Frame::Simple("no".into()),
                ])),
                "*" => {
                    let frame = Frame::Array(vec![
                        Frame::Simple("save".into()),
                        Frame::Bulk(Bytes::from("3600 1 300 100 60 10000")),
                        Frame::Simple("appendonly".into()),
                        Frame::Simple("no".into()),
                    ]);

                    Ok(frame)
                }
                _ => Ok(resp_err(REDIS_NOT_SUPPORTED_ERR)),
            }
        } else {
            Ok(resp_err(REDIS_NOT_SUPPORTED_ERR))
        }
    }
}
