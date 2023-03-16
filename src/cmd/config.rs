use std::sync::Arc;

use crate::cmd::{Invalid, Parse};
use crate::config::is_use_txn_api;
use crate::tikv::config::ConfigCommandCtx;
use crate::tikv::errors::{AsyncResult, REDIS_NOT_SUPPORTED_ERR};
use crate::utils::{resp_err, resp_invalid_arguments};
use crate::{Connection, Frame};

use crate::config::LOGGER;
use bytes::Bytes;
use slog::debug;
use tikv_client::Transaction;
use tokio::sync::Mutex;
#[derive(Debug, Clone)]
pub struct Config {
    key: String,
    field: String,
    valid: bool,
}

impl Config {
    pub fn new(key: &str, field: &str) -> Config {
        Config {
            field: field.to_owned(),
            key: key.to_owned(),
            valid: true,
        }
    }

    pub fn key(&self) -> &str {
        &self.key
    }

    pub fn field(&self) -> &str {
        &self.field
    }

    pub(crate) fn parse_frames(parse: &mut Parse) -> crate::Result<Config> {
        let key = parse.next_string()?;
        let field = parse.next_string()?;
        Ok(Config::new(&key, &field))
    }

    pub(crate) fn parse_argv(argv: &Vec<Bytes>) -> crate::Result<Config> {
        if argv.len() != 2 {
            return Ok(Config::new_invalid());
        }
        Ok(Config::new(
            &String::from_utf8_lossy(&argv[0]),
            &String::from_utf8_lossy(&argv[1]),
        ))
    }

    pub(crate) async fn apply(self, dst: &mut Connection) -> crate::Result<()> {
        let response = self.config(None).await?;
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

    pub async fn config(&self, txn: Option<Arc<Mutex<Transaction>>>) -> AsyncResult<Frame> {
        if !self.valid {
            return Ok(resp_invalid_arguments());
        }
        if !is_use_txn_api() {
            return Ok(resp_err(REDIS_NOT_SUPPORTED_ERR));
        }

        ConfigCommandCtx::new(txn)
            .do_async_rawkv_get(&self.key, &self.field)
            .await

        // match self.key.to_lowercase().as_str() {
        //     "get" => match self.field.to_lowercase().as_str() {
        //         "save" => {
        //             return Ok(Frame::Bulk(
        //                 Bytes::from("3600 1 300 100 60 10000").to_owned(),
        //             ));
        //         }
        //         "appendonly" => {
        //             return Ok(Frame::Bulk(Bytes::from("no".to_owned())));
        //         }
        //         _ => return Ok(Frame::Simple("no".to_owned())),
        //     },
        //     _ => Ok(Frame::Simple("OK".to_owned())),
        // }
    }
}

impl Invalid for Config {
    fn new_invalid() -> Config {
        Config {
            field: "".to_owned(),
            key: "".to_owned(),
            valid: false,
        }
    }
}
