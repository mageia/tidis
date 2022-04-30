use std::sync::Arc;

use crate::cmd::{Parse};
use crate::tikv::errors::AsyncResult;
use crate::tikv::hash::HashCommandCtx;
use crate::{Connection, Frame};
use crate::config::{is_use_txn_api};
use crate::utils::{resp_err, resp_invalid_arguments};

use tikv_client::Transaction;
use tokio::sync::Mutex;
use tracing::{debug, instrument};

#[derive(Debug)]
pub struct Hdel {
    key: String,
    field: String,
    valid: bool,
}

impl Hdel {
    pub fn new(key: &str, field: &str) -> Hdel {
        Hdel {
            field: field.to_owned(),
            key: key.to_owned(),
            valid: true,
        }
    }

    pub fn new_invalid() -> Hdel {
        Hdel {
            field: "".to_owned(),
            key: "".to_owned(),
            valid: false,
        }
    }

    pub fn key(&self) -> &str {
        &self.key
    }

    pub fn field(&self) -> &str {
        &self.field
    }

    pub(crate) fn parse_frames(parse: &mut Parse) -> crate::Result<Hdel> {
        let key = parse.next_string()?;
        let field = parse.next_string()?;
        Ok(Hdel::new(&key, &field))
    }

    pub(crate) fn parse_argv(argv: &Vec<String>) -> crate::Result<Hdel> {
        if argv.len() != 2 {
            return Ok(Hdel::new_invalid());
        }
        Ok(Hdel::new(&argv[0], &argv[1]))
    }

    #[instrument(skip(self, dst))]
    pub(crate) async fn apply(self, dst: &mut Connection) -> crate::Result<()> {
        
        let response = self.hdel(None).await?;
        debug!(?response);
        dst.write_frame(&response).await?;

        Ok(())
    }

    pub async fn hdel(&self, txn: Option<Arc<Mutex<Transaction>>>) -> AsyncResult<Frame> {
        if !self.valid {
            return Ok(resp_invalid_arguments());
        }
        if is_use_txn_api() {
            HashCommandCtx::new(txn).do_async_txnkv_hdel(&self.key, &self.field).await
        } else {
            Ok(resp_err("not supported yet"))
        }
    }
}
