#!/usr/bin/env runhaskell

{-# LANGUAGE OverloadedStrings #-}

import Text.Pandoc
import Numeric
import Data.Text(Text, unpack, pack, intercalate)
import Data.Char(ord)
import Text.Regex.TDFA
import qualified Data.Text.IO as T

mmdOutwardLinks :: Text -> IO Text 
mmdOutwardLinks txt = runIOorExplode $
    readMarkdown def{ readerExtensions=multimarkdownExtensions } txt
    >>= pure . getLinks

main :: IO ()
main = do
    T.getContents >>= mmdOutwardLinks >>= T.putStrLn

digit36 :: Char -> Int
digit36 x | x `elem` ['0'..'9'] = (ord x) - (ord '0')
          | x `elem` ['A'..'Z'] = (ord x) - (ord 'A')  + 10
          | x `elem` ['a'..'z'] = (ord x) - (ord 'a')  + 10

base36 :: String -> Int
base36 x = fst $ head $ readInt 36 (`elem` ['0'..'9']++['a'..'z']++['A'..'Z']) digit36 x

extractLink :: String -> [Int]
extractLink x | x =~ decRegex :: Bool = map base10 $ getMatches $ getResult decRegex x 
              | x =~ b36Regex :: Bool = map base36 $ getMatches $ getResult b36Regex x
              | otherwise = [] 
    where b36Regex = "^\\[\\[([0-9A-Za-z]{8})\\]\\]$"
          decRegex = "^\\[\\[([0-9]{12})\\]\\]$"
          getMatches (_, _, _, xs) = xs
          getResult :: String -> String -> (String, String, String, [String])
          getResult regex var = var =~ regex
          base10 x = read x :: Int

getLink :: Inline -> [Int]
getLink (Str txt) = extractLink $ unpack txt
getLink (Link _ xs target) = (extractLink $ unpack $ fst target) ++ getLink xs
getLink (Link _ [] target) = extractLink $ unpack $ fst target
getLink _ = []

getLinks :: Pandoc -> Text
getLinks p = intercalate " " $ map (pack.show) $ queryWith getLink p
