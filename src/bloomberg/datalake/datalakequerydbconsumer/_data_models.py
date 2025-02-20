"""
 ** Copyright 2021 Bloomberg Finance L.P.
 **
 ** Licensed under the Apache License, Version 2.0 (the "License");
 ** you may not use this file except in compliance with the License.
 ** You may obtain a copy of the License at
 **
 **     http://www.apache.org/licenses/LICENSE-2.0
 **
 ** Unless required by applicable law or agreed to in writing, software
 ** distributed under the License is distributed on an "AS IS" BASIS,
 ** WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 ** See the License for the specific language governing permissions and
 ** limitations under the License.
"""


from __future__ import annotations

from datetime import datetime
from typing import Any, TypeVar, cast

from dateutil import parser
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger

Base = declarative_base()

T = TypeVar("T")


class QueryMetrics(Base):  # type: ignore
    __tablename__ = "query_metrics"

    queryId = Column("queryId", String(100), primary_key=True)
    transactionId = Column("transactionId", String(100))
    query = Column("query", String(10000))
    remoteClientAddress = Column("remoteClientAddress", String(100))
    user = Column("user", String(100))
    userAgent = Column("userAgent", String(100))
    source = Column("source", String(100))
    serverAddress = Column("serverAddress", String(100))
    serverVersion = Column("serverVersion", String(100))
    environment = Column("environment", String(10))
    queryType = Column("queryType", String(50))
    cpuTime = Column("cpuTime", Float)
    wallTime = Column("wallTime", Float)
    queuedTime = Column("queuedTime", Float)
    scheduledTime = Column("scheduledTime", Float)
    analysisTime = Column("analysisTime", Float)
    planningTime = Column("planningTime", Float)
    executionTime = Column("executionTime", Float)
    peakUserMemoryBytes = Column("peakUserMemoryBytes", BigInteger)
    peakTotalNonRevocableMemoryBytes = Column("peakTotalNonRevocableMemoryBytes", BigInteger, nullable=True)
    peakTaskUserMemory = Column("peakTaskUserMemory", BigInteger)
    peakTaskTotalMemory = Column("peakTaskTotalMemory", BigInteger)
    physicalInputBytes = Column("physicalInputBytes", BigInteger)
    physicalInputRows = Column("physicalInputRows", BigInteger)
    internalNetworkBytes = Column("internalNetworkBytes", BigInteger)
    internalNetworkRows = Column("internalNetworkRows", BigInteger)
    totalBytes = Column("totalBytes", BigInteger)
    totalRows = Column("totalRows", BigInteger)
    outputBytes = Column("outputBytes", BigInteger)
    outputRows = Column("outputRows", BigInteger)
    writtenBytes = Column("writtenBytes", BigInteger)
    writtenRows = Column("writtenRows", BigInteger)
    cumulativeMemory = Column("cumulativeMemory", Float)
    completedSplits = Column("completedSplits", Integer)
    resourceWaitingTime = Column("resourceWaitingTime", Float)
    createTime = Column("createTime", DateTime)
    executionStartTime = Column("executionStartTime", DateTime)
    endTime = Column("endTime", DateTime)

    __table_args__ = {"schema": "raw_metrics", "extend_existing": True}


class ColumnMetrics(Base):  # type: ignore
    __tablename__ = "column_metrics"

    queryId = Column("queryId", String(100), ForeignKey(QueryMetrics.queryId), primary_key=True)
    catalogName = Column("catalogName", String(100), primary_key=True)
    schemaName = Column("schemaName", String(100), primary_key=True)
    tableName = Column("tableName", String(100), primary_key=True)
    columnName = Column("columnName", String(100), primary_key=True)
    physicalInputBytes = Column("physicalInputBytes", Integer)
    physicalInputRows = Column("physicalInputRows", Integer)

    __table_args__ = {"extend_existing": True, "schema": "raw_metrics"}

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ColumnMetrics):
            return False
        return cast(
            bool,
            self.queryId == other.queryId
            and self.catalogName == other.catalogName
            and self.schemaName == other.schemaName
            and self.tableName == other.tableName
            and self.columnName == other.columnName,
        )

    def __hash__(self) -> int:
        return hash(frozenset([self.queryId, self.catalogName, self.schemaName, self.tableName, self.columnName]))


def _get_datetime_from_field(field: str | int | float | datetime) -> datetime:
    if isinstance(field, float):
        return datetime.fromtimestamp(field)
    elif isinstance(field, int):
        return datetime.fromtimestamp(float(field))
    elif isinstance(field, str):
        return parser.parse(field)
    elif isinstance(field, datetime):
        return field
    else:
        raise TypeError(
            f"Invalid argument: {field=} should be a string, integer, float or datetime object, not {type(field)}"
        )


def get_query_metrics_from_raw(raw_metrics: dict[str, Any]) -> QueryMetrics:
    return QueryMetrics(
        queryId=raw_metrics["metadata"]["queryId"],
        transactionId=raw_metrics["metadata"]["transactionId"],
        query=raw_metrics["metadata"]["query"],
        queryType=raw_metrics["context"]["queryType"],
        remoteClientAddress=raw_metrics["context"]["remoteClientAddress"],
        user=raw_metrics["context"]["user"],
        userAgent=raw_metrics["context"]["userAgent"],
        source=raw_metrics["context"]["source"],
        serverAddress=raw_metrics["context"]["serverAddress"],
        serverVersion=raw_metrics["context"]["serverVersion"],
        environment=raw_metrics["context"]["environment"],
        cpuTime=raw_metrics["statistics"]["cpuTime"],
        wallTime=raw_metrics["statistics"]["wallTime"],
        queuedTime=raw_metrics["statistics"]["queuedTime"],
        scheduledTime=raw_metrics["statistics"]["scheduledTime"],
        analysisTime=raw_metrics["statistics"]["analysisTime"],
        planningTime=raw_metrics["statistics"]["planningTime"],
        executionTime=raw_metrics["statistics"]["executionTime"],
        peakUserMemoryBytes=raw_metrics["statistics"]["peakUserMemoryBytes"],
        peakTotalNonRevocableMemoryBytes=raw_metrics["statistics"].get("peakTotalNonRevocableMemoryBytes"),
        peakTaskUserMemory=raw_metrics["statistics"]["peakTaskUserMemory"],
        peakTaskTotalMemory=raw_metrics["statistics"]["peakTaskTotalMemory"],
        physicalInputBytes=raw_metrics["statistics"]["physicalInputBytes"],
        physicalInputRows=raw_metrics["statistics"]["physicalInputRows"],
        internalNetworkBytes=raw_metrics["statistics"]["internalNetworkBytes"],
        internalNetworkRows=raw_metrics["statistics"]["internalNetworkRows"],
        totalBytes=raw_metrics["statistics"]["totalBytes"],
        totalRows=raw_metrics["statistics"]["totalRows"],
        outputBytes=raw_metrics["statistics"]["outputBytes"],
        outputRows=raw_metrics["statistics"]["outputRows"],
        writtenBytes=raw_metrics["statistics"]["writtenBytes"],
        writtenRows=raw_metrics["statistics"]["writtenRows"],
        cumulativeMemory=raw_metrics["statistics"]["cumulativeMemory"],
        completedSplits=raw_metrics["statistics"]["completedSplits"],
        resourceWaitingTime=raw_metrics["statistics"]["resourceWaitingTime"],
        createTime=_get_datetime_from_field(raw_metrics["createTime"]),
        executionStartTime=_get_datetime_from_field(raw_metrics["executionStartTime"]),
        endTime=_get_datetime_from_field(raw_metrics["endTime"]),
    )


def get_column_metrics_from_raw(raw_metrics: dict[str, Any]) -> list[ColumnMetrics]:
    column_metrics = [
        ColumnMetrics(
            queryId=raw_metrics["metadata"]["queryId"],
            catalogName=table["catalogName"],
            schemaName=table["schema"],
            tableName=table["table"],
            columnName=column,
            physicalInputBytes=table["physicalInputBytes"],
            physicalInputRows=table["physicalInputRows"],
        )
        for table in raw_metrics["ioMetadata"]["inputs"]
        for column in table["columns"]
    ]

    # Trino may send a column multiple times with the same information
    return list(dict.fromkeys(column_metrics))
