use std::sync::Arc;

use crate::cmd::{Invalid, Parse};
use crate::config::is_use_txn_api;
use crate::tikv::errors::{AsyncResult, REDIS_NOT_SUPPORTED_ERR};
use crate::tikv::hash::HashCommandCtx;
use crate::utils::{resp_err, resp_invalid_arguments};
use crate::{Connection, Frame};

use crate::config::LOGGER;
use bytes::Bytes;
use slog::debug;
use tikv_client::Transaction;
use tokio::sync::Mutex;

#[derive(Debug, Clone)]
pub struct Hincrby {
    key: String,
    field: String,
    step: i64,
    valid: bool,
}

impl Hincrby {
    pub fn new(key: &str, field: &str, step: i64) -> Hincrby {
        Hincrby {
            key: key.to_string(),
            field: field.to_string(),
            step,
            valid: true,
        }
    }

    /// Get the key
    pub fn key(&self) -> &str {
        &self.key
    }

    pub fn field(&self) -> &str {
        &self.field
    }

    pub fn set_key(&mut self, key: &str) {
        self.key = key.to_owned();
    }

    pub fn set_field(&mut self, field: &str) {
        self.field = field.to_owned();
    }

    pub(crate) fn parse_frames(parse: &mut Parse) -> crate::Result<Hincrby> {
        let key = parse.next_string()?;
        let field = parse.next_string()?;
        let step = parse.next_int()?;
        Ok(Hincrby {
            key,
            field,
            step,
            valid: true,
        })
    }

    pub(crate) fn parse_argv(argv: &Vec<Bytes>) -> crate::Result<Hincrby> {
        if argv.len() != 3 {
            return Ok(Hincrby::new_invalid());
        }
        let key = &String::from_utf8_lossy(&argv[0]);
        let field = &String::from_utf8_lossy(&argv[1]);
        let step = String::from_utf8_lossy(&argv[2]).parse::<i64>();
        match step {
            Ok(v) => Ok(Hincrby::new(key, field, v)),
            Err(_) => Ok(Hincrby::new_invalid()),
        }
    }

    pub(crate) async fn apply(self, dst: &mut Connection) -> crate::Result<()> {
        let response = self.hincrby(None).await?;
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

    pub async fn hincrby(&self, txn: Option<Arc<Mutex<Transaction>>>) -> AsyncResult<Frame> {
        if !self.valid {
            return Ok(resp_invalid_arguments());
        }
        if is_use_txn_api() {
            HashCommandCtx::new(txn)
                .do_async_txnkv_hincrby(&self.key, &self.field, self.step)
                .await
        } else {
            Ok(resp_err(REDIS_NOT_SUPPORTED_ERR))
        }
    }
}

impl Invalid for Hincrby {
    fn new_invalid() -> Hincrby {
        Hincrby {
            key: "".to_string(),
            field: "".to_string(),
            step: 0,
            valid: false,
        }
    }
}
