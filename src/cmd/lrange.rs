use std::sync::Arc;

use crate::cmd::{Invalid, Parse};
use crate::config::is_use_txn_api;
use crate::tikv::errors::{AsyncResult, REDIS_NOT_SUPPORTED_ERR};
use crate::tikv::list::ListCommandCtx;
use crate::utils::{resp_err, resp_invalid_arguments};
use crate::{Connection, Frame};

use crate::config::LOGGER;
use bytes::Bytes;
use slog::debug;
use tikv_client::Transaction;
use tokio::sync::Mutex;

#[derive(Debug, Clone)]
pub struct Lrange {
    key: String,
    left: i64,
    right: i64,
    valid: bool,
}

impl Lrange {
    pub fn new(key: &str, left: i64, right: i64) -> Lrange {
        Lrange {
            key: key.to_owned(),
            left,
            right,
            valid: true,
        }
    }

    pub fn key(&self) -> &str {
        &self.key
    }

    pub(crate) fn parse_frames(parse: &mut Parse) -> crate::Result<Lrange> {
        let key = parse.next_string()?;
        let left = parse.next_int()?;
        let right = parse.next_int()?;

        Ok(Lrange {
            key,
            left,
            right,
            valid: true,
        })
    }

    pub(crate) fn parse_argv(argv: &Vec<Bytes>) -> crate::Result<Lrange> {
        if argv.len() != 3 {
            return Ok(Lrange::new_invalid());
        }
        let key = &String::from_utf8_lossy(&argv[0]);
        let left = match String::from_utf8_lossy(&argv[1]).parse::<i64>() {
            Ok(v) => v,
            Err(_) => return Ok(Lrange::new_invalid()),
        };

        let right = match String::from_utf8_lossy(&argv[2]).parse::<i64>() {
            Ok(v) => v,
            Err(_) => return Ok(Lrange::new_invalid()),
        };
        Ok(Lrange::new(key, left, right))
    }

    pub(crate) async fn apply(self, dst: &mut Connection) -> crate::Result<()> {
        let response = self.lrange(None).await?;
        debug!(
            LOGGER,
            "res, {} -> {}, {:?}",
            dst.local_addr(),
            dst.peer_addr(),
            response
        );
        dst.write_frame(&response).await?;

        Ok(())
    }

    pub async fn lrange(&self, txn: Option<Arc<Mutex<Transaction>>>) -> AsyncResult<Frame> {
        if !self.valid {
            return Ok(resp_invalid_arguments());
        }
        if is_use_txn_api() {
            ListCommandCtx::new(txn)
                .do_async_txnkv_lrange(&self.key, self.left, self.right)
                .await
        } else {
            Ok(resp_err(REDIS_NOT_SUPPORTED_ERR))
        }
    }
}

impl Invalid for Lrange {
    fn new_invalid() -> Lrange {
        Lrange {
            key: "".to_owned(),
            left: 0,
            right: 0,
            valid: false,
        }
    }
}
