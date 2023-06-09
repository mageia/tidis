use std::sync::Arc;

use crate::cmd::{Invalid, Parse};
use crate::config::is_use_txn_api;
use crate::tikv::errors::{AsyncResult, REDIS_NOT_SUPPORTED_ERR};
use crate::tikv::set::SetCommandCtx;
use crate::utils::{resp_err, resp_invalid_arguments};
use crate::{Connection, Frame};

use crate::config::LOGGER;
use bytes::Bytes;
use slog::debug;
use tikv_client::Transaction;
use tokio::sync::Mutex;

#[derive(Debug, Clone)]
pub struct Sismember {
    key: String,
    member: String,
    valid: bool,
}

impl Sismember {
    pub fn new(key: &str, member: &str) -> Sismember {
        Sismember {
            key: key.to_string(),
            member: member.to_string(),
            valid: true,
        }
    }

    pub(crate) fn parse_frames(parse: &mut Parse) -> crate::Result<Sismember> {
        let key = parse.next_string()?;
        let member = parse.next_string()?;
        Ok(Sismember {
            key,
            member,
            valid: true,
        })
    }

    pub(crate) fn parse_argv(argv: &Vec<Bytes>) -> crate::Result<Sismember> {
        if argv.len() != 2 {
            return Ok(Sismember::new_invalid());
        }
        Ok(Sismember::new(
            &String::from_utf8_lossy(&argv[0]),
            &String::from_utf8_lossy(&argv[1]),
        ))
    }

    pub(crate) async fn apply(self, dst: &mut Connection) -> crate::Result<()> {
        let response = self.sismember(None).await?;
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

    pub async fn sismember(&self, txn: Option<Arc<Mutex<Transaction>>>) -> AsyncResult<Frame> {
        if !self.valid {
            return Ok(resp_invalid_arguments());
        }
        if is_use_txn_api() {
            let mut members = vec![];
            members.push(self.member.clone());
            SetCommandCtx::new(txn)
                .do_async_txnkv_sismember(&self.key, &members, false)
                .await
        } else {
            Ok(resp_err(REDIS_NOT_SUPPORTED_ERR))
        }
    }
}

impl Invalid for Sismember {
    fn new_invalid() -> Sismember {
        Sismember {
            key: "".to_string(),
            member: "".to_string(),
            valid: false,
        }
    }
}
