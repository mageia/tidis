use std::sync::Arc;

use crate::cmd::{Invalid, Parse};
use crate::config::is_use_txn_api;
use crate::tikv::errors::{AsyncResult, REDIS_NOT_SUPPORTED_ERR};
use crate::tikv::zset::ZsetCommandCtx;
use crate::utils::{resp_err, resp_invalid_arguments};
use crate::{Connection, Frame};

use crate::config::LOGGER;
use bytes::Bytes;
use slog::debug;
use tikv_client::Transaction;
use tokio::sync::Mutex;

#[derive(Debug, Clone)]
pub struct Zrank {
    key: String,
    member: String,
    valid: bool,
}

impl Zrank {
    pub fn new(key: &str, member: &str) -> Zrank {
        Zrank {
            key: key.to_string(),
            member: member.to_string(),
            valid: true,
        }
    }

    pub(crate) fn parse_frames(parse: &mut Parse) -> crate::Result<Zrank> {
        let key = parse.next_string()?;
        let member = parse.next_string()?;

        Ok(Zrank {
            key,
            member,
            valid: true,
        })
    }

    pub(crate) fn parse_argv(argv: &Vec<Bytes>) -> crate::Result<Zrank> {
        if argv.len() != 2 {
            return Ok(Zrank::new_invalid());
        }
        Ok(Zrank::new(
            &String::from_utf8_lossy(&argv[0]),
            &String::from_utf8_lossy(&argv[1]),
        ))
    }

    pub(crate) async fn apply(self, dst: &mut Connection) -> crate::Result<()> {
        let response = self.zrank(None).await?;
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

    pub async fn zrank(&self, txn: Option<Arc<Mutex<Transaction>>>) -> AsyncResult<Frame> {
        if !self.valid {
            return Ok(resp_invalid_arguments());
        }
        if is_use_txn_api() {
            ZsetCommandCtx::new(txn)
                .do_async_txnkv_zrank(&self.key, &self.member)
                .await
        } else {
            Ok(resp_err(REDIS_NOT_SUPPORTED_ERR))
        }
    }
}

impl Invalid for Zrank {
    fn new_invalid() -> Zrank {
        Zrank {
            key: "".to_string(),
            member: "".to_string(),
            valid: false,
        }
    }
}
