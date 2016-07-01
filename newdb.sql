-- MySQL dump 10.13  Distrib 5.5.49, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: cce
-- ------------------------------------------------------
-- Server version	5.5.49-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `address`
--

DROP TABLE IF EXISTS `address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `address` (
  `address` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT 'Not Available',
  `balance` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `n_tx` int(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`address`),
  KEY `balance` (`balance`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `adminSignatures`
--

DROP TABLE IF EXISTS `adminSignatures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `adminSignatures` (
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  `version` mediumint(9) NOT NULL DEFAULT '0',
  `adminId` varchar(10) COLLATE utf8_bin NOT NULL DEFAULT 'undef',
  `signature` varchar(148) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`height`,`adminId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `block`
--

DROP TABLE IF EXISTS `block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `block` (
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  `hash` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `time` int(10) NOT NULL DEFAULT '0',
  `creator` varchar(10) COLLATE utf8_bin NOT NULL DEFAULT 'undef',
  `nSignatures` mediumint(9) NOT NULL DEFAULT '0',
  `nAdminSignatures` mediumint(9) NOT NULL DEFAULT '0',
  `payload` varchar(32) COLLATE utf8_bin NOT NULL DEFAULT '',
  `creatorSignature` varchar(148) COLLATE utf8_bin NOT NULL DEFAULT '',
  `size` mediumint(9) NOT NULL DEFAULT '0',
  `version` int(11) NOT NULL DEFAULT '0',
  `merkleroot` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `total_fee` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `n_tx` tinyint(4) NOT NULL DEFAULT '0',
  `total_sent` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `raw` text COLLATE utf8_bin,
  PRIMARY KEY (`height`),
  KEY `hash` (`hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chainParameter`
--

DROP TABLE IF EXISTS `chainParameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chainParameter` (
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  `version` int(11) NOT NULL DEFAULT '0',
  `minAdminSigs` mediumint(9) NOT NULL DEFAULT '0',
  `maxAdminSigs` mediumint(9) NOT NULL DEFAULT '0',
  `blockSpacing` mediumint(9) NOT NULL DEFAULT '0',
  `blockSpacingGracePeriod` mediumint(9) NOT NULL DEFAULT '0',
  `transactionFee` int(16) NOT NULL DEFAULT '0',
  `dustThreshold` int(16) NOT NULL DEFAULT '0',
  `minSuccessiveSignatures` mediumint(9) NOT NULL DEFAULT '0',
  PRIMARY KEY (`height`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cvn`
--

DROP TABLE IF EXISTS `cvn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cvn` (
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  `nodeId` varchar(10) COLLATE utf8_bin NOT NULL DEFAULT 'undef',
  `heightAdded` mediumint(9) NOT NULL DEFAULT '-1',
  `pubKey` varchar(148) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`height`,`nodeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cvnalias`
--

DROP TABLE IF EXISTS `cvnalias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cvnalias` (
  `nodeId` varchar(10) COLLATE utf8_bin NOT NULL DEFAULT 'undef',
  `alias` varchar(32) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`nodeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cvnstatus`
--

DROP TABLE IF EXISTS `cvnstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cvnstatus` (
  `nodeId` varchar(10) COLLATE utf8_bin NOT NULL DEFAULT 'undef',
  `heightAdded` mediumint(9) NOT NULL DEFAULT '-1',
  `pubKey` varchar(148) COLLATE utf8_bin NOT NULL DEFAULT '',
  `predictedNextBlock` mediumint(9) NOT NULL DEFAULT '-1',
  `lastBlocksSigned` mediumint(8) NOT NULL DEFAULT '-1',
  PRIMARY KEY (`nodeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `large_tx`
--

DROP TABLE IF EXISTS `large_tx`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `large_tx` (
  `tx` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `amount` decimal(16,8) NOT NULL DEFAULT '0.00000000'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `orph_block`
--

DROP TABLE IF EXISTS `orph_block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orph_block` (
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  `hash` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `time` int(10) NOT NULL DEFAULT '0',
  `creator` varchar(10) COLLATE utf8_bin NOT NULL DEFAULT 'undef',
  `nSignatures` mediumint(9) NOT NULL DEFAULT '0',
  `nAdminSignatures` mediumint(9) NOT NULL DEFAULT '0',
  `payload` varchar(32) COLLATE utf8_bin NOT NULL DEFAULT '',
  `creatorSignature` varchar(148) COLLATE utf8_bin NOT NULL DEFAULT '',
  `size` mediumint(9) NOT NULL DEFAULT '0',
  `version` int(11) NOT NULL DEFAULT '0',
  `merkleroot` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `total_fee` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `n_tx` tinyint(4) NOT NULL DEFAULT '0',
  `total_sent` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `raw` text COLLATE utf8_bin,
  KEY `hash` (`hash`),
  KEY `height` (`height`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `orph_tx_in`
--

DROP TABLE IF EXISTS `orph_tx_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orph_tx_in` (
  `tx_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `coinbase` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `prev_out_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `vout` int(4) NOT NULL DEFAULT '0',
  `asm` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `hex` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `value_in` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `address` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `height` mediumint(9) NOT NULL DEFAULT '0',
  KEY `address` (`address`),
  KEY `height` (`height`),
  KEY `tx_hash` (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `orph_tx_out`
--

DROP TABLE IF EXISTS `orph_tx_out`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orph_tx_out` (
  `tx_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `n` int(4) NOT NULL DEFAULT '0',
  `value` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `type` varchar(50) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `address` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `asm` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `height` mediumint(9) NOT NULL DEFAULT '0',
  KEY `address` (`address`),
  KEY `height` (`height`),
  KEY `tx_hash` (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `orph_tx_raw`
--

DROP TABLE IF EXISTS `orph_tx_raw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orph_tx_raw` (
  `tx_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `raw` mediumtext COLLATE utf8_bin,
  `decoded` mediumtext COLLATE utf8_bin NOT NULL,
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  UNIQUE KEY `tx_hash` (`tx_hash`),
  KEY `height` (`height`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `peers`
--

DROP TABLE IF EXISTS `peers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `peers` (
  `IP` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `version` int(10) NOT NULL DEFAULT '0',
  `connection` varchar(16) COLLATE utf8_bin NOT NULL DEFAULT '',
  `sub` varchar(32) COLLATE utf8_bin NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `signatures`
--

DROP TABLE IF EXISTS `signatures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `signatures` (
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  `version` mediumint(9) NOT NULL DEFAULT '0',
  `signerId` varchar(10) COLLATE utf8_bin NOT NULL DEFAULT 'undef',
  `signature` varchar(148) COLLATE utf8_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`height`,`signerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stats`
--

DROP TABLE IF EXISTS `stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stats` (
  `total_mint` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `peers` int(4) NOT NULL DEFAULT '0',
  `peer_txt` text COLLATE utf8_bin NOT NULL,
  `cvns` int(4) NOT NULL DEFAULT '0',
  `cvn_txt` text COLLATE utf8_bin NOT NULL,
  `db_version` decimal(4,2) NOT NULL DEFAULT '4.10',
  PRIMARY KEY (`db_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `top_address`
--

DROP TABLE IF EXISTS `top_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `top_address` (
  `rank` smallint(3) NOT NULL DEFAULT '0',
  `address` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT ' Not Available',
  `balance` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `n_tx` int(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`rank`),
  KEY `rank` (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tx_in`
--

DROP TABLE IF EXISTS `tx_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tx_in` (
  `tx_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `coinbase` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `prev_out_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `vout` int(4) NOT NULL DEFAULT '0',
  `asm` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `hex` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `value_in` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `address` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `height` mediumint(9) NOT NULL DEFAULT '0',
  KEY `address` (`address`),
  KEY `height` (`height`),
  KEY `tx_hash` (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tx_out`
--

DROP TABLE IF EXISTS `tx_out`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tx_out` (
  `tx_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `n` int(4) NOT NULL DEFAULT '0',
  `value` decimal(16,8) NOT NULL DEFAULT '0.00000000',
  `type` varchar(50) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `address` varchar(64) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `asm` varchar(256) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `height` mediumint(9) NOT NULL DEFAULT '0',
  KEY `address` (`address`),
  KEY `height` (`height`),
  KEY `tx_hash` (`tx_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tx_raw`
--

DROP TABLE IF EXISTS `tx_raw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tx_raw` (
  `tx_hash` varchar(65) COLLATE utf8_bin NOT NULL DEFAULT '0',
  `raw` mediumtext COLLATE utf8_bin,
  `decoded` mediumtext COLLATE utf8_bin NOT NULL,
  `height` mediumint(9) NOT NULL DEFAULT '-1',
  UNIQUE KEY `tx_hash` (`tx_hash`),
  KEY `height` (`height`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-07-01 16:11:07
